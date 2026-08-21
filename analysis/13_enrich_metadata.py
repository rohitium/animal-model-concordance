"""Enrich each study with full PubMed metadata: MeSH terms, publication types,
DOI, abstract, funding, and author list. All from efetch XML, no inference."""
import sys, os, json, re, time, urllib.request, html as _html
ROOT = os.path.join(os.path.dirname(__file__), "..")
db = json.load(open(os.path.join(ROOT, "data", "db", "studies.json")))
pmids = list(db)

def txt(s):
    """Strip markup then UNESCAPE. PubMed encodes accented characters as numeric
    entities (&#xf3;); leaving them escaped puts raw entity codes on the page."""
    t = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()

out = {}
for i in range(0, len(pmids), 100):
    ch = pmids[i:i+100]
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
           + ",".join(ch) + "&tool=animal-model-concordance&email=rsatija@stanford.edu")
    xml = None
    for a in range(4):
        try:
            xml = urllib.request.urlopen(url, timeout=120).read().decode("utf-8", "replace"); break
        except Exception: time.sleep(2 ** a)
    if not xml: continue
    # Each record must be bounded by its OWN closing tag. Splitting on the opening
    # tag alone lets a chunk run to the end of the document, so a record lacking
    # <ArticleTitle> (book chapters) picks up the next article's title -- silently
    # attaching the wrong title to a PMID.
    chunks = (re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.S)
              + re.findall(r"<PubmedBookArticle>.*?</PubmedBookArticle>", xml, re.S))
    for art in chunks:
        m = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
        if not m: continue
        pm = m.group(1)
        mesh = []
        for blk in re.findall(r"<MeshHeading>(.*?)</MeshHeading>", art, re.S):
            d = re.search(r'<DescriptorName[^>]*?(MajorTopicYN="Y")?[^>]*>(.*?)</DescriptorName>', blk, re.S)
            if not d: continue
            quals = [txt(q) for q in re.findall(r"<QualifierName[^>]*>(.*?)</QualifierName>", blk, re.S)]
            mesh.append({"term": txt(d.group(2)), "major": bool(d.group(1)), "qualifiers": quals})
        # Only the primary <Abstract>. Journals such as Dialogues in Clinical
        # Neuroscience publish Spanish and French translations in <OtherAbstract>;
        # matching <AbstractText> anywhere concatenated all three languages.
        _main = re.search(r"<Abstract>(.*?)</Abstract>", art, re.S)
        _scope = _main.group(1) if _main else ""
        abst = " ".join(txt(a0) for a0 in
                        re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", _scope, re.S))
        secs = [(txt(lbl), txt(body)) for lbl, body in
                re.findall(r'<AbstractText[^>]*Label="([^"]+)"[^>]*>(.*?)</AbstractText>', _scope, re.S)]
        _other = re.findall(r'<OtherAbstract[^>]*Language="([^"]+)"', art)
        doi = re.search(r'<ArticleId IdType="doi">(.*?)</ArticleId>', art, re.S)
        pmc = re.search(r'<ArticleId IdType="pmc">(.*?)</ArticleId>', art, re.S)
        ti = (re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", art, re.S)
              or re.search(r"<BookTitle[^>]*>(.*?)</BookTitle>", art, re.S))
        out[pm] = {
            "mesh": mesh,
            "publication_types": [txt(x) for x in re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", art, re.S)],
            "doi": txt(doi.group(1)) if doi else None,
            "pmcid": txt(pmc.group(1)) if pmc else None,
            "abstract": abst,
            "abstract_sections": secs,
            "title": txt(ti.group(1)) if ti else "",
            "is_book": "<BookTitle" in art,
            "other_languages": _other,
            "journal_full": (txt((re.search(r"<Title>(.*?)</Title>", art, re.S) or [None, ""])[1])
                             if re.search(r"<Title>(.*?)</Title>", art, re.S)
                             else txt((re.search(r"<PublisherName[^>]*>(.*?)</PublisherName>", art, re.S) or [None,""])[1])
                                  if re.search(r"<PublisherName[^>]*>(.*?)</PublisherName>", art, re.S) else ""),
            "authors_full": [f"{txt(l)} {txt(f)}".strip() for f, l in
                             re.findall(r"<Author[^>]*>.*?<LastName>(.*?)</LastName>.*?<ForeName>(.*?)</ForeName>", art, re.S)][:40],
            "grants": sorted({txt(a0) for a0 in re.findall(r"<Agency>(.*?)</Agency>", art, re.S)}),
            "country": txt((re.search(r"<Country>(.*?)</Country>", art, re.S) or [None,""])[1]) if re.search(r"<Country>(.*?)</Country>", art, re.S) else None,
        }
    print(f"  enriched {len(out)}/{len(pmids)}")

json.dump(out, open(os.path.join(ROOT, "data", "db", "metadata.json"), "w"), indent=1)
nm = sum(1 for v in out.values() if v["mesh"])
print(f"\nmetadata for {len(out)} studies; {nm} have MeSH indexing")
