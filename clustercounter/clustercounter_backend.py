from flask import send_file
from PIL import Image
import io
import base64
import numpy as np
import cv2
import copy
from skimage.feature import peak_local_max
import zipfile
import scipy.ndimage as ndimage
import os
import pandas as pd
from skimage import measure
from functools import lru_cache

global globaldf
globaldf = pd.DataFrame()

## ClusterAnalysis class
class ClusterAnalysis:

    def __init__(self, czifile, czifilearray):

        self.czifile = czifile
        self.czifilearray = czifilearray

        self.clusterchannelarray = None
        self.clusterchannelarray8bit = None

        self.aischannelarray = None
        self.aischannelarray8bit = None

        self.thresharray = None

        self.thresh_ROI_nn = None

        self.bgarray = None
        self.bgimage = None

        self.fgarray = None
        self.fgimage = None

        self.resetROI = None

    def arraytoimage(self, array):
        clusterarrayimage = Image.fromarray(array)
        rawBytes = io.BytesIO()
        clusterarrayimage.save(rawBytes, "JPEG")
        rawBytes.seek(0)
        image = str(base64.b64encode(rawBytes.read()).decode("utf-8"))
        return image

    def cleardf(self):
        global globaldf
        globaldf = pd.DataFrame()
        print("Cleared Results")

    def filter_isolated_cells(self, array, struct):
        """ Return array with completely isolated single cells removed
        :param array: Array with completely isolated single cells
        :param struct: Structure array for generating unique regions
        :return: Array with minimum region size > 1
        """

        filtered_array = np.copy(array)
        id_regions, num_ids = ndimage.label(filtered_array, structure=struct)
        id_sizes = np.array(ndimage.sum(array, id_regions, range(num_ids + 1)))
        area_mask = (id_sizes == 255)
        filtered_array[area_mask[id_regions]] = 0
        return filtered_array

    @lru_cache(maxsize=1)
    def createclusterchannel(self, clusterchannelindex):
        clusterchannelarray = self.czifilearray[0, 0, int(clusterchannelindex), 0, 0, :, :, 0]
        clusterchannelarray8bit = (clusterchannelarray / (255)).astype('uint8')
        print('created cluster channel')

        self.createthresh.cache_clear()
        self.createbg.cache_clear()
        self.createfgdt.cache_clear()
        self.createfgm.cache_clear()
        self.createresults.cache_clear()

        return clusterchannelarray, clusterchannelarray8bit

    @lru_cache(maxsize=1)
    def createaischannel(self, aischannelindex):
        aischannelarray = self.czifilearray[0, 0, int(aischannelindex), 0, 0, :, :, 0]
        aischannelarray8bit = (aischannelarray / (255)).astype('uint8')
        print('created AIS channel')

        self.createthresh.cache_clear()
        self.createbg.cache_clear()
        self.createfgdt.cache_clear()
        self.createfgm.cache_clear()
        self.createresults.cache_clear()

        return aischannelarray8bit

    @lru_cache(maxsize=1)
    def createthresh(self, threshindex, checkbox, ):
        ret1, thresharray = cv2.threshold(self.clusterchannelarray8bit, int(threshindex), 255, cv2.THRESH_BINARY)
        print("created thresh")

        self.createbg.cache_clear()
        self.createfgdt.cache_clear()
        self.createfgm.cache_clear()
        self.createresults.cache_clear()

        if checkbox == '1':
            thresharray = self.filter_isolated_cells(thresharray, struct=np.ones((3, 3)))

        return thresharray

    def createthreshROI(self, coordsnp):
        mask = np.zeros(self.thresharray.shape[0:2], dtype=np.uint8)
        cv2.drawContours(mask, [coordsnp], -1, (255, 255, 255), -1, cv2.LINE_AA)
        self.thresharray = cv2.bitwise_and(self.thresharray, self.thresharray, mask=mask)
        print("created thresh ROi")

        self.createbg.cache_clear()
        self.createfgdt.cache_clear()
        self.createfgm.cache_clear()
        self.createresults.cache_clear()

    @lru_cache(maxsize=1)
    def createthreshROI_RC(self, ROIdilateindex, ROIthreshindex):
        ret4, thresh_ROI = cv2.threshold(self.aischannelarray8bit,
                                         ((int(ROIthreshindex)) / 100) * self.aischannelarray8bit.max(), 255, 0)
        kernel2 = np.ones((3, 3), np.uint8)
        thresh_ROI_nn = cv2.morphologyEx(thresh_ROI, cv2.MORPH_OPEN, kernel2)
        kernel3 = np.ones((3, 3), np.uint8)
        thresh_ROI_nn = cv2.dilate(thresh_ROI_nn, kernel3, iterations=int(ROIdilateindex))
        self.thresharray[thresh_ROI_nn == 0] = 0
        thresharray = self.thresharray
        print('createdthreshROI_RC')

        self.createbg.cache_clear()
        self.createfgdt.cache_clear()
        self.createfgm.cache_clear()
        self.createresults.cache_clear()

        return thresh_ROI_nn, thresharray

    @lru_cache(maxsize=1)
    def createbg(self, bgindex):
        kernel = np.ones((3, 3), np.uint8)
        number_of_dilations = int(bgindex)
        bgarray = cv2.dilate(self.thresharray, kernel, iterations=number_of_dilations)
        print('created bg')

        self.createresults.cache_clear()

        return bgarray

    @lru_cache(maxsize=1)
    def createfgdt(self, fgindexdtthresh, fgindexdterosion):

        dist_transform = cv2.distanceTransform(self.thresharray, cv2.DIST_L2, 3)
        ret2, sure_fg = cv2.threshold(dist_transform, ((int(fgindexdtthresh)) / 100) * dist_transform.max(), 255, 0)
        kernel1 = np.ones((2, 2), np.uint8)
        sure_fg = cv2.erode(sure_fg, kernel1, iterations=int(fgindexdterosion))
        fgarray = np.uint8(sure_fg)
        print('created fgdt')

        self.createresults.cache_clear()

        return fgarray

    @lru_cache(maxsize=1)
    def createfgm(self, minimumdistance):

        cluster_peaks = copy.copy(self.clusterchannelarray8bit)
        cluster_peaks[self.thresharray == 0] = 0
        cluster_peaks1 = peak_local_max(cluster_peaks, min_distance=int(minimumdistance))

        for i in range(cluster_peaks1.shape[0]):
            cv2.circle(cluster_peaks, (cluster_peaks1[i][1], cluster_peaks1[i][0]), 0, 255)

        ret2, fgarray = cv2.threshold(cluster_peaks, 254, 255, 0)
        print('created fgm')

        self.createresults.cache_clear()

        return fgarray

    @lru_cache(maxsize=1)
    def createresults(self, currentactivatedpanel, add, pxum):
        watershedarray = cv2.cvtColor(self.clusterchannelarray8bit, cv2.COLOR_GRAY2RGB)
        unknown = cv2.subtract(self.bgarray, self.fgarray)
        ret3, markers = cv2.connectedComponents(self.fgarray)
        print(np.max(markers))
        markers += 10
        markers[unknown == 255] = 0

        if currentactivatedpanel == '1':
            markers = cv2.watershed(watershedarray, markers)

        if currentactivatedpanel == '2':
            thresh = cv2.cvtColor(self.thresharray, cv2.COLOR_GRAY2RGB)
            markers = cv2.watershed(thresh, markers)

        watershedarray[markers == (-1)] = [255, 105, 180]
        print(np.shape(watershedarray))
        print('created results')

        if add:
            props = measure.regionprops_table(markers, self.clusterchannelarray,
                                              properties=['label',
                                                          'area', 'equivalent_diameter',
                                                          'mean_intensity', 'solidity', 'orientation',
                                                          'perimeter'])

            data = pd.DataFrame(props)

            # data = data[data['area'] > 1]
            data['label'] = data['label'] - 10
            data = data[data['label'] > 0]

            data['area_sq_microns'] = data['area'] * (float(pxum) ** 2)
            data['equivalent_diameter_microns'] = data['equivalent_diameter'] * (float(pxum))
            data.insert(0, str(self.czifile.filename), "")
            data.insert(0, '', "")

            summary = {'infoname': ["",
                                    'number of clusters',
                                    'mean area (px)',
                                    'mean area (µm)',
                                    'mean diameter (px)',
                                    'mean diameter (µm)',
                                    'mean intensity'],
                       'info': ["",
                                data['label'].max(),
                                data['area'].mean(),
                                data['area_sq_microns'].mean(),
                                data['equivalent_diameter'].mean(),
                                data['equivalent_diameter_microns'].mean(),
                                data['mean_intensity'].mean()]}
            summary = pd.DataFrame(data=summary)
            summary.insert(0, '', "")
            data = pd.concat([data, summary], axis=1)

            print(data)

            global globaldf
            globaldf = pd.concat([globaldf, data], axis=1)

            print("added data")

        return watershedarray

    def showclusterchannel(self, clusterchannelindex):
        (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
        self.resetROI = True
        clusterchannelimage = self.arraytoimage(self.clusterchannelarray8bit)
        return clusterchannelimage

    def showaischannel(self, aischannelindex):
        (self.aischannelarray8bit) = self.createaischannel(aischannelindex)
        aischannelimage = self.arraytoimage(self.aischannelarray8bit)
        return aischannelimage

    def showthreshchannel(self, clusterchannelindex, threshindex, checkbox, ignoreif):
        (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
        if ignoreif:
            self.createthresh.cache_clear()
        self.thresharray = self.createthresh(threshindex, checkbox)
        self.resetROI = True
        threshimage = self.arraytoimage(self.thresharray)
        return threshimage

    def showcutthreshchannel(self, clusterchannelindex, threshindex, checkbox, coords):
        self.resetROI = False
        (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
        self.thresharray = self.createthresh(threshindex, checkbox)
        coordsnp = np.empty((0, 2), int)

        while (np.size(coords) > 0):
            coordsnp = np.concatenate((coordsnp, [coords[0:2]]), axis=0)
            coords = np.delete(coords, [0, 1])

        self.createthreshROI(coordsnp)

        threshimage = self.arraytoimage(self.thresharray)
        return threshimage

    def showroichannelcutthreshchannel(self, clusterchannelindex, threshindex, checkbox, aischannelindex,
                                       ROIdilateindex,
                                       ROIthreshindex, viewroi):
        if self.resetROI:
            (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
            self.thresharray = self.createthresh(threshindex, checkbox)
        self.aischannelarray8bit = self.createaischannel(aischannelindex)
        (thresh_ROI_nn, self.thresharray) = self.createthreshROI_RC(ROIdilateindex, ROIthreshindex)

        self.resetROI = False
        if viewroi:
            thresh_ROI_image = self.arraytoimage(thresh_ROI_nn)
            return thresh_ROI_image
        else:
            threshimage = self.arraytoimage(self.thresharray)
            return threshimage

    def showbgchannel(self, clusterchannelindex, threshindex, checkbox, bgindex):
        if self.resetROI:
            (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
            self.thresharray = self.createthresh(threshindex, checkbox)
        self.bgarray = self.createbg(bgindex)

        bgimage = self.arraytoimage(self.bgarray)
        return bgimage

    def showfgdtchannel(self, clusterchannelindex, threshindex, checkbox, fgindexdtthresh, fgindexdterosion):
        if self.resetROI:
            (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
            self.thresharray = self.createthresh(threshindex, checkbox)
        self.fgarray = self.createfgdt(fgindexdtthresh, fgindexdterosion)

        fgimage = self.arraytoimage(self.fgarray)
        return fgimage

    def showfgmchannel(self, clusterchannelindex, threshindex, checkbox, minimumdistance):
        if self.resetROI:
            (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
            self.thresharray = self.createthresh(threshindex, checkbox)
        self.fgarray = self.createfgm(minimumdistance)

        fgimage = self.arraytoimage(self.fgarray)
        return fgimage

    def performanalysis(self, currentactivatedpanel, threshindex, clusterchannelindex, bgindex, fgindexdtthresh,
                        fgindexdterosion, minimumdistance, checkbox, add, pxum):
        if self.resetROI:
            (self.clusterchannelarray, self.clusterchannelarray8bit) = self.createclusterchannel(clusterchannelindex)
            self.thresharray = self.createthresh(threshindex, checkbox)
        self.bgarray = self.createbg(bgindex)
        if currentactivatedpanel == '1':
            self.fgarray = self.createfgdt(fgindexdtthresh, fgindexdterosion)
        elif currentactivatedpanel == '2':
            self.fgarray = self.createfgm(minimumdistance)
        watershedarray = self.createresults(currentactivatedpanel, add, pxum)
        cv2.imshow("", watershedarray)
        cv2.waitKey()
        watershedimage = self.arraytoimage(watershedarray)
        return watershedimage

    def downloadresults(self):

        exceldf = io.BytesIO()
        globaldf.to_excel(exceldf)
        exceldf.seek(0)  # may not be necessary?
        return send_file(
            exceldf,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            attachment_filename='data.xlsx',
            cache_timeout=-1
        )

    def downloadzip(self):

        def generate_tiff(rawimage):

            image = Image.fromarray(rawimage)
            rawBytes = io.BytesIO()
            image.save(rawBytes, "TIFF")
            # rawBytes.seek(0)
            imagebytes = rawBytes.getvalue()
            rawBytes.close()
            return imagebytes

        file_names = ["clusterchannelimage.tiff", "ROIchannelimage.tiff", "threshimage.tiff", "backgroundimage.tiff",
                      "foregroungimage.tiff",
                      "watershedimage.tiff"]
        images = [self.clusterchannelarray, self.aischannelarray, self.thresharray,
                  self.bgarray, self.fgarray,
                  self.watershedimage]
        files = []

        for index in range(len(images)):
            if images[index] is not None:
                tiff = generate_tiff(images[index])  # your file generation method goes here
                files.append((file_names[index], tiff))

        mem_zip = io.BytesIO()

        with zipfile.ZipFile(mem_zip, mode="w") as zf:
            for f in files:
                zf.writestr(f[0], f[1])

        mem_zip.seek(0)

        return send_file(
            mem_zip,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename=os.path.splitext(self.czifile.filename)[0] + '.zip',
            cache_timeout=-1
        )

