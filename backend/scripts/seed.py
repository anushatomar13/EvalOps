"""Populate the database with a realistic demo workspace.

Creates a user, a couple of projects, prompt versions, a dataset, and several
evaluation runs across models/configs so the dashboard and Compare view have
data immediately.

Run from the backend dir:  python -m scripts.seed
Login afterwards with:     demo@evalforge.dev / demo1234
"""
import random

from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.dataset import Dataset, DatasetItem
from app.models.evaluation import EvalRun
from app.models.project import Project
from app.models.prompt import PromptVersion
from app.models.user import User
from app.services.eval_runner import run_evaluation

DEMO_EMAIL = "demo@evalforge.dev"
DEMO_PASSWORD = "demo1234"

QUESTIONS = [
    ("What is EMI?", "EMI is the fixed monthly payment a borrower makes to repay a loan."),
    ("How is interest calculated on a loan?", "Interest = principal × rate × time, applied per the schedule."),
    ("What is compound interest?", "Interest calculated on principal plus previously accrued interest."),
    ("What is a credit score?", "A number summarizing creditworthiness based on credit history."),
    ("What is loan tenure?", "The total duration over which a loan is to be repaid."),
    ("What is a down payment?", "An upfront partial payment made when taking a loan."),
    ("What is the difference between APR and interest rate?", "APR includes fees; the interest rate does not."),
    ("What is loan default?", "Failure to repay a loan according to the agreed terms."),
    ("What is collateral?", "An asset pledged to secure a loan."),
    ("What is a fixed vs floating rate?", "Fixed stays constant; floating varies with a benchmark."),
    ("What is prepayment?", "Paying off part or all of a loan before the due date."),
    ("What is an amortization schedule?", "A table showing each payment split into principal and interest."),
]


def reset():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def main():
    reset()
    db = SessionLocal()
    try:
        user = User(
            email=DEMO_EMAIL,
            full_name="Demo User",
            hashed_password=hash_password(DEMO_PASSWORD),
            is_admin=True,
        )
        db.add(user)
        db.flush()

        project = Project(
            name="Loan Assistant",
            description="RAG-based assistant answering retail-loan questions.",
            task_type="rag",
            owner_id=user.id,
        )
        db.add(project)
        db.flush()

        prompts = []
        for i, (content, note) in enumerate(
            [
                ("You are a loan assistant. Answer concisely.", "initial"),
                ("You are a loan assistant. Answer concisely and cite the source.", "added citations"),
                (
                    "You are a careful loan assistant. Answer concisely, cite the source, and refuse if unsure.",
                    "added refusal guardrail",
                ),
            ],
            start=1,
        ):
            p = PromptVersion(project_id=project.id, version=i, content=content, notes=note)
            db.add(p)
            prompts.append(p)

        dataset = Dataset(
            project_id=project.id, name="finance", version=1, description="Retail loan Q&A", row_count=len(QUESTIONS)
        )
        db.add(dataset)
        db.flush()
        for q, gt in QUESTIONS:
            db.add(DatasetItem(dataset_id=dataset.id, question=q, ground_truth=gt))
        db.flush()

        # A series of runs that tell a story: model upgrades + prompt iterations.
        run_specs = [
            ("llama baseline", "llama", 0.2, prompts[0], "dense"),
            ("gpt-4.1 v1", "gpt-4.1", 0.2, prompts[0], "hybrid"),
            ("gpt-4.1 v2 prompt", "gpt-4.1", 0.2, prompts[1], "hybrid"),
            ("claude v3 prompt", "claude", 0.2, prompts[2], "hybrid"),
            ("gpt-4.1 hot temp", "gpt-4.1", 0.8, prompts[2], "hybrid"),
        ]
        run_ids = []
        for name, model, temp, prompt, retriever in run_specs:
            run = EvalRun(
                project_id=project.id,
                dataset_id=dataset.id,
                prompt_version_id=prompt.id,
                name=name,
                status="queued",
                git_commit=f"{random.randint(0x100000, 0xffffff):06x}",
                config={
                    "model": model,
                    "temperature": temp,
                    "embedding": "bge-large",
                    "retriever": retriever,
                    "chunk_size": 512,
                    "top_k": 5,
                },
            )
            db.add(run)
            db.flush()
            run_ids.append(run.id)
        db.commit()

        for rid in run_ids:
            run_evaluation(rid, db)

        print("Seed complete.")
        print(f"  Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  Project: {project.name} (id={project.id}) with {len(run_ids)} runs")
    finally:
        db.close()


if __name__ == "__main__":
    main()
