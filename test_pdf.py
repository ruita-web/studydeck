from pypdf import PdfReader

# Look for your actual file name!
reader = PdfReader("What-is-Social-Media-Marketing.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() or ""

print(f"✅ Success! Got {len(text)} characters from {len(reader.pages)} pages")
print("\n--- First 500 chars ---\n")
print(text[:500])