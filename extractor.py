from bs4 import BeautifulSoup


def extract_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # 🏷️ Extract title
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    body = ""

    # 📰 1️⃣ Try to extract <article class="tts_ok"> first
    article = soup.find("article", class_="tts_ok")
    if article:
        text_lines = [
            line.strip()
            for line in article.get_text(separator="\n").splitlines()
            if line.strip()
        ]
        body = " ".join(text_lines)

    # 🧱 2️⃣ Fallback to any <article> if specific class not found
    else:
        article = soup.find("article")
        if article:
            text_lines = [
                line.strip()
                for line in article.get_text(separator="\n").splitlines()
                if line.strip()
            ]
            body = " ".join(text_lines)

        # 🧱 3️⃣ Final fallback to <body>
        elif soup.body:
            text_lines = [
                line.strip()
                for line in soup.body.get_text(separator="\n").splitlines()
                if line.strip()
            ]
            body = " ".join(text_lines)

    return title, body
