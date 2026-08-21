import sys, os, urllib.request, re, time
sys.path.insert(0, os.path.dirname(__file__))
P = ["17032985","18772421","19297654","21097827","22460880","21892149","24678540","20361020","23401516"]
url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
       + ",".join(P) + "&tool=animal-model-concordance&email=rsatija@stanford.edu")
xml = urllib.request.urlopen(url, timeout=90).read().decode()
for art in xml.split("<PubmedArticle>")[1:]:
    pmid = re.search(r"<PMID[^>]*>(\d+)</PMID>", art).group(1)
    mh = re.findall(r"<DescriptorName[^>]*>([^<]+)</DescriptorName>", art)
    pt = re.findall(r"<PublicationType[^>]*>([^<]+)</PublicationType>", art)
    print(f"\n{pmid}  types={pt}")
    print("   MeSH:", "; ".join(mh) if mh else "(none)")
