import os
import cv2
import numpy as np
import math


class PageManage:
    def __init__(self, bShow=False):
        self.blur_kernel = (3, 3)

        self.thresh_block_sz = 11

        self.canny_range = (50, 110)
        self.canny_apertureSZ = 3
        self.bShow = bShow

        self.line_color = (0, 0, 255)
        self.line_thickness = 30

    #
    def proc_page(self, page_path):
        gray = cv2.imread(page_path, cv2.IMREAD_GRAYSCALE)
        gray = cv2.blur(gray, self.blur_kernel)
        # os.remove(page_path)

        crop = self.__crop_page(gray=gray)

        lines = self.__line_detect(gray=crop)

        pages = self.__split_page(page=crop, lines=lines)

        if self.bShow:
            show_img = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
            if lines is not None and len(lines) != 0:
                for [[x1, y1, x2, y2]] in lines:
                    print((x1, y1), (x2, y2))
                    cv2.line(show_img, (x1, y1), (x2, y2), self.line_color, self.line_thickness)
            cv2.imshow("line", cv2.resize(show_img, (300, 700)))
            cv2.waitKey(0)
        return pages

    #
    def __crop_page(self, gray):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, self.thresh_block_sz, 2)
        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            # find only parent contours
            parents = []
            for i in range(len(contours)):
                [next, previous, first_child, parent] = hierarchy[0][i]
                if first_child != -1:
                    parents.append(contours[i])

            if len(parents) != 0:
                # find the biggest area
                max_contour = max(parents, key=cv2.contourArea)
                border_rect = cv2.boundingRect(max_contour)
            else:
                max_contour = max(contours, key=cv2.contourArea)
                border_rect = cv2.boundingRect(max_contour)

            x, y, w, h = border_rect
            crop = gray[:, x: x + w]
            return crop
        return gray

    #
    def __line_detect(self, gray):
        height, width = gray.shape[:2]

        canny = cv2.Canny(gray, self.canny_range[0], self.canny_range[1], apertureSize=self.canny_apertureSZ)

        _min_line_len = int(width * 0.8)
        _threshold = int(_min_line_len)
        _max_line_gap = int(width / 5)
        lines = cv2.HoughLinesP(canny,
                                rho=1,
                                theta=np.pi / 2,
                                threshold=_threshold,
                                minLineLength=_min_line_len,
                                maxLineGap=_max_line_gap)

        if lines is not None and len(lines) != 0:
            candi_lines = []
            for line in lines:
                [[x1, y1, x2, y2]] = line
                if math.fabs(y1 - y2) < math.fabs(x1 - x2):
                    candi_lines.append(line)
            return candi_lines

    #
    def __split_page(self, page, lines):
        height, width = page.shape[:2]
        if lines is not None and len(lines) != 0:
            lines_y = []
            for [[x1, y1, x2, y2]] in lines:
                lines_y.append((y1 + y2) / 2)
            lines_y.sort()

            i = 0
            sub_pages = []
            sub_heights = []
            sub_widths = []

            start_y, end_y = None, None
            while i < len(lines_y):
                if start_y is None:
                    start_y = lines_y[i]
                elif math.fabs(start_y - lines_y[i]) < width / 5:
                    start_y = lines_y[i]
                else:
                    end_y = lines_y[i]
                    sub_page = page[start_y + 10: end_y - 10]
                    sub_pages.append(sub_page)
                    start_y = end_y
                    sub_heights.append(sub_page.shape[0])
                    sub_widths.append(sub_page.shape[1])

                i += 1

            ones = np.ones((max(sub_heights), max(sub_widths)), dtype=np.uint8) * 255
            new_pages = []
            for sub_page in sub_pages:
                new_page = ones.copy()
                new_page[:sub_page.shape[0], :sub_page.shape[1]] = sub_page
                new_pages.append(new_page)

                if self.bShow:
                    cv2.imshow("page", cv2.resize(new_page, (300, 500)))
                    cv2.waitKey(1000)
            return new_pages
