import numpy as np

def differentiateObject(depthMap,threshold,pixOffset):
    xRange=a.shape[0]
    yRange=a.shape[1]
    tempArr=np.array(shape=(xRange,yRange), dtype=bool)
    boundPix=False
    perimeter=0
    for x in range(0,xRange):
        for y in range(0,yRange):
            if depthMap[x,y]-depthMap[x,(y-pixOffset)]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[x,(y+pixOffset)]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[(x-pixOffset),y]>threshold:
                boundPix=True
            if depthMap[x,y]-depthMap[(x+pixOffset),y]>threshold:
                boundPix=True
            if boundPix:
                tempArr[x,y] = True
                perimeter+=1
    return tempArr
 
