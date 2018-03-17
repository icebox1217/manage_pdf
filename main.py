from config import *

from src.pdf_utils import PdfUtils
from src.page_manage import PageManage

if __name__ == '__main__':
    pdf_path = "./data/sample_pdf_long3.pdf"
    if os.path.splitext(pdf_path)[1] in DOC_EXT:
        sys.stdout.write("converting the pdf to images...\n")
        image_paths = PdfUtils().pdfTojpgs(pdf_path=pdf_path)

        sys.stdout.write("split the page images ...\n")
        pages = PageManage().proc_page(page_path=image_paths[0])
        # pages = PageManage(bShow=False).proc_page(page_path="./data/sample_pdf_long3-1.jpg")

        sys.stdout.write("create new pdf file ...\n")
        tail, fn = os.path.split(pdf_path)
        tar_pdf_path = os.path.join(tail, "new_" + fn)
        nums = PdfUtils().imgsTopdf(cv_imgs=pages, pdf_path=tar_pdf_path)
