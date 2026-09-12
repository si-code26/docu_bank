"""Generate fake data per-user, per-year"""

import random
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).parent / "data" / "fake_pdfs"
FEES_BY_YEAR = {2025: "1%", 2026: "2%"}
USERS = [f"user{i}" for i in range(1,11)]
random.seed(42)

def make_pdf(user: str, year: int) -> None:
    user_dir = OUTPUT_DIR / user
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"faq-{year}.pdf"
    
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 16)
    c.drawString(72, 720, f"DocuBank Policy FAQ - {year}")
    
    c.setFont("Helvetica", 11)
    lines = [
        f"Account holder: {user}",
        f"Effective year: {year}",
        "",
        f"Overdraft fee: {FEES_BY_YEAR[year]} of the overdrawn amount",
        f"Monthly maintence fee: ${random.randint(5,15)}.00",
        f"ATM withdrawal limit: ${random.choice([300,500,1000])} per day",
        f"Wire transfer fee: ${random.randint(10,30)}.00 per transfer.",
        "Contact support for questions about your account"
    ]
    y = 680
    for line in lines:
        c.drawString(72,y,line)
        y -= 18

    c.save()
    print(f"wrote {path}")

def main() -> None:
    for user in USERS:
        for year in FEES_BY_YEAR:
            make_pdf(user, year)
    print(f"done: {len(USERS) * len(FEES_BY_YEAR)} PDFs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()


