import cv2
import numpy as np


class PageManage:
    def __init__(self, bShow=True):
        self.blur_kernel = (3, 3)

        self.thresh_block_sz = 11

        self.canny_range = (50, 110)
        self.canny_apertureSZ = 3
        self.bShow = bShow

        self.line_color = (0, 0, 255)
        self.line_thickness = 3

    def proc_page(self, page_path):
        gray = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)

        gray = cv2.blur(gray, self.blur_kernel)
        crop = self.__crop_page(gray=gray)
        lines = self.__line_detect(gray=crop)

        if self.bShow:
            show_img = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
            for [[x1, y1, x2, y2]] in lines:
                print((x1, y1), (x2, y2))
                cv2.line(show_img, (x1, y1), (x2, y2), self.line_color, self.line_thickness)
            cv2.imwrite("line.jpg", show_img)

    #
    def __crop_page(self, gray):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, self.thresh_block_sz, 2)
        cv2.imwrite("thresh.jpg", thresh)
        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            # find the biggest area
            max_contour = max(contours, key=cv2.contourArea)
            cv2.boundingRect(max_contour)

            coors_x = []
            coors_y = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                coors_x.extend([x, x + w])
                coors_y.extend([y, y + h])

            x, y, w, h = [min(coors_x), min(coors_y), max(coors_x), max(coors_y)]
            crop = gray[y: y + h, x: x + w]
            return crop
        return gray

    #
    def __line_detect(self, gray):
        height, width = gray.shape[:2]

        canny = cv2.Canny(gray, self.canny_range[0], self.canny_range[1], apertureSize=self.canny_apertureSZ)
        cv2.imwrite("canny.jpg", canny)

        _min_line_len = int(width * 0.8)
        _threshold = int(_min_line_len / 2)
        _max_line_gap = int(width / 5)
        lines = cv2.HoughLinesP(canny,
                                rho=1,
                                theta=np.pi / 2,
                                threshold=_threshold,
                                minLineLength=_min_line_len,
                                maxLineGap=_max_line_gap)

        return lines