from flask import send_file, jsonify
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
from flask import session
import czifile
from math import sqrt

## ClusterAnalysis class
class ClusterAnalysis:

    def __init__(self):

        session["CC_DataFrame"] = pd.DataFrame()
        session["CC_currentfileslist"] = []



    def showrgbimage(self, czifile, czifilearray):
        session["czifilename"] = czifile.filename
        session["czifilearray"] = czifilearray
        array = czifilearray[0, 0, :, 0, 0, :, :, 0]
        array = (array / (255)).astype('uint8')
        r = array[0, :, :]
        g = array[1, :, :]
        b = array[2, :, :]
        array = np.dstack((r, g, b))
        rgbimage = Image.fromarray(array, 'RGB')
        rawBytes = io.BytesIO()
        rgbimage.save(rawBytes, "JPEG")
        rawBytes.seek(0)
        image = str(base64.b64encode(rawBytes.read()).decode("utf-8"))

        # if session.get("CC_thresharray") is not "":
        session.pop("CC_clusterchannelarray", None)
        session.pop("CC_clusterchannelarray8bit", None)
        session.pop("CC_aischannelarray8bit", None)
        session.pop("CC_tresharray", None)
        session.pop("CC_resetROI", None)
        session.pop("CC_thresh_ROI_nn", None)
        session.pop("CC_bgarray", None)
        session.pop("CC_fgarray", None)
        session.pop("CC_watershedimage", None)
        session.pop("CC_coordsmask", None)
        session.pop("CC_isline", None)
        session.pop("CC_linelength", None)

        session["CC_resetROI"] = True

        return image

    def finddistance(self, points):
        summarize = []

        for index, point in enumerate(points):

            if index + 1 != len(points):
                x1 = point[0]
                y1 = point[1]
                x2 = points[index + 1][0]
                y2 = points[index + 1][1]

                distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                summarize.append(distance)

        totaldistance = sum(summarize)

        return totaldistance

    def arraytoimage(self, array):
        clusterarrayimage = Image.fromarray(array)
        rawBytes = io.BytesIO()
        clusterarrayimage.save(rawBytes, "JPEG")
        rawBytes.seek(0)
        image = str(base64.b64encode(rawBytes.read()).decode("utf-8"))
        return image

    def cleardf(self):
        session["CC_DataFrame"] = pd.DataFrame()
        session["CC_currentfileslist"] = []
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


    def createclusterchannel(self, clusterchannelindex):
        clusterchannelarray = session.get("czifilearray")[0, 0, int(clusterchannelindex), 0, 0, :, :, 0]
        clusterchannelarray8bit = (clusterchannelarray / (255)).astype('uint8')
        print('created cluster channel')

        return clusterchannelarray, clusterchannelarray8bit

    def createaischannel(self, aischannelindex):
        aischannelarray = session.get("czifilearray")[0, 0, int(aischannelindex), 0, 0, :, :, 0]
        session["CC_aischannelarray"] = aischannelarray
        aischannelarray8bit = (aischannelarray / (255)).astype('uint8')
        print('created AIS channel')

        return aischannelarray8bit

    def createthresh(self, threshindex, checkbox, ):
        ret1, thresharray = cv2.threshold(session["CC_clusterchannelarray8bit"], int(threshindex), 255, cv2.THRESH_BINARY)
        print("created thresh")

        if checkbox == '1':
            thresharray = self.filter_isolated_cells(thresharray, struct=np.ones((3, 3)))

        return thresharray

    def createthreshROI(self, coordsnp, analysisoption):
        mask = np.zeros(session["CC_tresharray"].shape[0:2], dtype=np.uint8)
        cv2.drawContours(mask, [coordsnp], -1, (255, 255, 255), -1, cv2.LINE_AA)
        if analysisoption == '1':
            session["CC_tresharray"] = cv2.bitwise_and(session["CC_clusterchannelarray8bit"], session["CC_clusterchannelarray8bit"], mask=mask)

        else:
            session["CC_tresharray"] = cv2.bitwise_and(session["CC_tresharray"], session["CC_tresharray"], mask=mask)

        session["CC_coordsmask"] = mask
        print("created thresh ROi")

    def createthreshLine(self, coordsnp, linewidth):
        mask = np.zeros(session["CC_tresharray"].shape[0:2], dtype=np.uint8)
        mask = cv2.polylines(mask, [coordsnp], False, (255,255,255), int(linewidth))
        cv2.imshow('kk', mask)
        cv2.waitKey()
        print(coordsnp)

        session["CC_tresharray"] = cv2.bitwise_and(session["CC_tresharray"], session["CC_tresharray"], mask=mask)

        session["CC_coordsmask"] = mask
        session["CC_isline"] = True
        session["CC_linelength"] = self.finddistance(coordsnp)
        print("created thresh line, Distance:", session["CC_linelength"])

    def createthreshROI_RC(self, ROIdilateindex, ROIthreshindex, analysisoption, ROIgaussianindex):
        blurredROIarray = cv2.GaussianBlur(session["CC_aischannelarray8bit"], (0, 0), int(ROIgaussianindex))
        ret4, thresh_ROI = cv2.threshold(blurredROIarray,
                                         ((int(ROIthreshindex)) / 100) * blurredROIarray.max(), 255, 0)
        kernel2 = np.ones((3, 3), np.uint8)
        thresh_ROI_nn = cv2.morphologyEx(thresh_ROI, cv2.MORPH_OPEN, kernel2)
        kernel3 = np.ones((3, 3), np.uint8)
        thresh_ROI_nn = cv2.dilate(thresh_ROI_nn, kernel3, iterations=int(ROIdilateindex))
        if "CC_coordsmask" in session:
            thresh_ROI_nn = cv2.bitwise_and(thresh_ROI_nn, thresh_ROI_nn, mask = session["CC_coordsmask"])
        session["CC_tresharray"][thresh_ROI_nn == 0] = 0
        print('createdthreshROI_RC')

        return thresh_ROI_nn

    def createbg(self, bgindex):
        kernel = np.ones((3, 3), np.uint8)
        number_of_dilations = int(bgindex)
        bgarray = cv2.dilate(session["CC_tresharray"], kernel, iterations=number_of_dilations)
        print('created bg')

        return bgarray

    def createfgdt(self, fgindexdtthresh, fgindexdterosion):

        dist_transform = cv2.distanceTransform(session["CC_tresharray"], cv2.DIST_L2, 3)
        ret2, sure_fg = cv2.threshold(dist_transform, ((int(fgindexdtthresh)) / 100) * dist_transform.max(), 255, 0)
        kernel1 = np.ones((2, 2), np.uint8)
        sure_fg = cv2.erode(sure_fg, kernel1, iterations=int(fgindexdterosion))
        fgarray = np.uint8(sure_fg)
        print('created fgdt')

        return fgarray

    def createfgm(self, minimumdistance):

        cluster_peaks = copy.copy(session["CC_clusterchannelarray8bit"])
        cluster_peaks[session["CC_tresharray"] == 0] = 0
        cluster_peaks1 = peak_local_max(cluster_peaks, min_distance=int(minimumdistance))

        for i in range(cluster_peaks1.shape[0]):
            cv2.circle(cluster_peaks, (cluster_peaks1[i][1], cluster_peaks1[i][0]), 0, 255)

        ret2, fgarray = cv2.threshold(cluster_peaks, 254, 255, 0)
        print('created fgm')

        return fgarray

    def createresults(self, currentactivatedpanel, add, pxum, analysisoption):
        watershedarray = cv2.cvtColor(session["CC_clusterchannelarray8bit"], cv2.COLOR_GRAY2RGB)
        if analysisoption == '1':
            markers = np.ones(session['CC_tresharray'].shape, dtype=np.uint8)
            markers[session['CC_tresharray'] == 0] = 0
            mask = copy.copy(markers)
            markers = markers + 10
            ctns = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            ctns = ctns[0] if len(ctns) == 2 else ctns[1]
            for c in ctns:
                cv2.drawContours(mask, [c], -1, 255, 1)
            watershedarray[mask == 255] = [255, 105, 180]
            print(np.shape(mask))

        else:
            unknown = cv2.subtract(session["CC_bgarray"], session["CC_fgarray"])
            ret3, markers = cv2.connectedComponents(session["CC_fgarray"])
            print(np.max(markers))
            markers += 10
            markers[unknown == 255] = 0

            if currentactivatedpanel == '1':
                markers = cv2.watershed(watershedarray, markers)

            if currentactivatedpanel == '2':
                thresh = cv2.cvtColor(session["CC_tresharray"], cv2.COLOR_GRAY2RGB)
                markers = cv2.watershed(thresh, markers)

            watershedarray[markers == (-1)] = [255, 105, 180]

        print(np.shape(watershedarray))
        print('created results')

        if add:
            props = measure.regionprops_table(markers, session["CC_clusterchannelarray"],
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
            data.insert(0, str(session["czifilename"]), "")
            data.insert(0, '', "")
            session["CC_currentfileslist"].append(session["czifilename"])

            if not session.get("CC_resetroi") and analysisoption == "0" and "CC_thresh_ROI_nn" in session:
                markers = np.ones(session['CC_thresh_ROI_nn'].shape, dtype=np.uint8)
                markers[session['CC_thresh_ROI_nn'] == 0] = 0
                propsROI = measure.regionprops(markers, session["CC_clusterchannelarray"])
                summary = {'infoname': ["",
                                        'number of clusters',
                                        'mean area (px)',
                                        'mean area (µm)',
                                        'mean diameter (px)',
                                        'mean diameter (µm)',
                                        'mean intensity',
                                        'ROI area (px)',
                                        'ROI area (µm)',
                                        'ROI mean intensity'],
                           'info': ["",
                                    data['label'].max(),
                                    data['area'].mean(),
                                    data['area_sq_microns'].mean(),
                                    data['equivalent_diameter'].mean(),
                                    data['equivalent_diameter_microns'].mean(),
                                    data['mean_intensity'].mean(),
                                    propsROI[0].area,
                                    propsROI[0].area * (float(pxum) ** 2),
                                    propsROI[0].mean_intensity]}
                summary = pd.DataFrame(data=summary)
                summary.insert(0, '', "")
                data = pd.concat([data, summary], axis=1)
            else:
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


            session["CC_DataFrame"] = pd.concat([session["CC_DataFrame"], data], axis=1)

            print("added data")

        session["CC_watershedimage"] = watershedarray
        return watershedarray

    def showclusterchannel(self, clusterchannelindex):
        (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
        session["CC_resetROI"] = True
        clusterchannelimage = self.arraytoimage(session["CC_clusterchannelarray8bit"])
        return clusterchannelimage

    def showaischannel(self, aischannelindex):
        (session["CC_aischannelarray8bit"]) = self.createaischannel(aischannelindex)
        aischannelimage = self.arraytoimage(session["CC_aischannelarray8bit"])
        return aischannelimage

    def showthreshchannel(self, clusterchannelindex, threshindex, checkbox, ignoreif, analysisoption):
        (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
        if analysisoption =='1':
            threshimage = self.arraytoimage(session["CC_clusterchannelarray8bit"])
            return threshimage
        else:
            if ignoreif == '0':
                session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
                session.pop("CC_coordsmask", None)
            if not "CC_tresharray" in session:
                session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
            session["CC_resetROI"] = True
            session.pop("CC_thresh_ROI_nn", None)
            threshimage = self.arraytoimage(session["CC_tresharray"])
            return threshimage

    def showcutthreshchannel(self, clusterchannelindex, threshindex, checkbox, coords, analysisoption, ifline, linewidth):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        if not "CC_tresharray" in session:
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)

        coordsnp = np.empty((0, 2), int)

        session["CC_resetROI"] = False
        while (np.size(coords) > 0):
            coordsnp = np.concatenate((coordsnp, [coords[0:2]]), axis=0)
            coords = np.delete(coords, [0, 1])
        if ifline:
            self.createthreshLine(coordsnp,linewidth)
        else:
            self.createthreshROI(coordsnp, analysisoption)

        threshimage = self.arraytoimage(session["CC_tresharray"])
        return threshimage

    def showroichannelcutthreshchannel(self, clusterchannelindex, threshindex, checkbox, aischannelindex,
                                       ROIdilateindex,
                                       ROIthreshindex, viewroi, analysisoption, ROIgaussianindex):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            if analysisoption == '1':
                session["CC_tresharray"] = session["CC_clusterchannelarray8bit"]
                print("thresharray set to clusterarray")
            else:
                session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        if not "CC_tresharray" in session:
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        session["CC_aischannelarray8bit"] = self.createaischannel(aischannelindex)
        thresh_ROI_nn = self.createthreshROI_RC(ROIdilateindex, ROIthreshindex, analysisoption, ROIgaussianindex)
        session["CC_thresh_ROI_nn"] = thresh_ROI_nn

        session["CC_resetROI"] = False
        if viewroi:
            thresh_ROI_image = self.arraytoimage(thresh_ROI_nn)
            return thresh_ROI_image
        else:
            threshimage = self.arraytoimage(session["CC_tresharray"])
            return threshimage

    def showbgchannel(self, clusterchannelindex, threshindex, checkbox, bgindex):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        session["CC_bgarray"] = self.createbg(bgindex)

        bgimage = self.arraytoimage(session["CC_bgarray"])
        return bgimage

    def showfgdtchannel(self, clusterchannelindex, threshindex, checkbox, fgindexdtthresh, fgindexdterosion):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        session["CC_fgarray"] = self.createfgdt(fgindexdtthresh, fgindexdterosion)

        fgimage = self.arraytoimage(session["CC_fgarray"])
        return fgimage

    def showfgmchannel(self, clusterchannelindex, threshindex, checkbox, minimumdistance):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        session["CC_fgarray"] = self.createfgm(minimumdistance)

        fgimage = self.arraytoimage(session["CC_fgarray"])
        return fgimage

    def performanalysis(self, currentactivatedpanel, threshindex, clusterchannelindex, bgindex, fgindexdtthresh,
                        fgindexdterosion, minimumdistance, checkbox, add, pxum, analysisoption):
        if session["CC_resetROI"]:
            (session["CC_clusterchannelarray"], session["CC_clusterchannelarray8bit"]) = self.createclusterchannel(clusterchannelindex)
            session["CC_tresharray"] = self.createthresh(threshindex, checkbox)
        if analysisoption == '0':
            session["CC_bgarray"] = self.createbg(bgindex)
            if currentactivatedpanel == '1':
                session["CC_fgarray"] = self.createfgdt(fgindexdtthresh, fgindexdterosion)
            elif currentactivatedpanel == '2':
                session["CC_fgarray"] = self.createfgm(minimumdistance)
        watershedarray = self.createresults(currentactivatedpanel, add, pxum, analysisoption)
        watershedimage = self.arraytoimage(watershedarray)
        return watershedimage

    def downloadresults(self):

        exceldf = io.BytesIO()
        session["CC_DataFrame"].to_excel(exceldf)
        exceldf.seek(0)  # may not be necessary?
        if session["sessionname"] == "":
            name = session["user"]
        else:
            name = session["sessionname"]
        return send_file(
            exceldf,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            attachment_filename= name+'.xlsx',
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
                      "foregroundimage.tiff",
                      "watershedimage.tiff"]
        images = [session.get("CC_clusterchannelarray"), session.get("CC_aischannelarray"), session.get("CC_tresharray"),
                  session.get("CC_bgarray"), session.get("CC_fgarray"),
                  session.get("CC_watershedimage")]
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
            attachment_filename=session["sessionname"] + "_" + os.path.splitext(session["czifilename"])[0] + '.zip',
            cache_timeout=-1
        )

    def viewcurrentfileslist(self):
        return session["CC_currentfileslist"]

