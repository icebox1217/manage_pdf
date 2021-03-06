import io
import numpy as np
import cv2
from PIL import Image
from wand.image import Image as WandImage
from wand.color import Color as WandColor
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from config import *


class PdfUtils:
    def __init__(self, resolution=300):
        self.resolution = resolution  # DPI

    def pdfTojpgs(self, pdf_path):
        if not os.path.exists(pdf_path):
            sys.stderr.write("No exist such pdf file {}\n".format(pdf_path))
            sys.exit(1)

        base, ext = os.path.splitext(pdf_path)
        if ext.lower() in DOC_EXT:  # pdf
            page_imgs = self.pdf2imgs_wand(pdf_path)
            paths = []
            for id in range(len(page_imgs)):
                img = page_imgs[id]
                img_path = base + "-" + str(id + 1) + ".jpg"
                cv2.imwrite(img_path, img)
                paths.append(img_path)
            # sys.stdout.write("\tpages: # {}\n".format(len(paths)))
            return paths
        else:
            sys.stderr.write("Not defined file type.\n")
            sys.exit(1)

    def pdf2imgs_wand(self, _pdf_path):
        images = []
        reader = PdfFileReader(open(_pdf_path, "rb"))

        for page_num in range(reader.getNumPages()):
            src_page = reader.getPage(page_num)

            dst_pdf = PdfFileWriter()
            dst_pdf.addPage(src_page)

            pdf_bytes = io.BytesIO()
            dst_pdf.write(pdf_bytes)
            pdf_bytes.seek(0)

            with WandImage(file=pdf_bytes, resolution=self.resolution) as wand_img:
                # convert wand image to nd_array cv
                wand_img.background_color = WandColor('white')
                wand_img.format = 'tif'
                wand_img.alpha_channel = False
                img_buffer = np.asarray(bytearray(wand_img.make_blob()), dtype=np.uint8)

            if img_buffer is not None:
                cv_img = cv2.imdecode(img_buffer, cv2.IMREAD_GRAYSCALE)
            images.append(cv_img)
        return images

    #
    def imgsTopdf(self, cv_imgs, pdf_path, quality=100):
        num = 0
        merger = PdfFileMerger()
        base, ext = os.path.splitext(pdf_path)

        for idx in range(len(cv_imgs)):
            page = cv_imgs[idx]
            pil_img = Image.fromarray(page)
            pil_img.info['dpi'] = (self.resolution, self.resolution)

            # write the each page to individual pdf file
            path = "{}_{}{}".format(base, str(idx), ext)
            pil_img.save(path, "PDF", resolution=int(self.resolution * (quality / 100)))

            # merge the separate pdf files to single one
            merger.append(PdfFileReader(path), "rb")
            os.remove(path)

            sys.stdout.write("\r   writing the page {} ...".format(idx + 1))
            sys.stdout.flush()
            num += 1
        merger.write(pdf_path)
        return num


if __name__ == '__main__':
    pdfPath = '../data/020294-0020843.pdf'
    image_paths = PdfUtils().pdfTojpgs(pdfPath)
    print(image_paths)
