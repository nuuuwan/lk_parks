from lk_parks.metadata.MetaDataBase import MetaDataBase
from lk_parks.metadata.MetaDataBasePlantNet import MetaDataBasePlantNet
from lk_parks.metadata.MetaDataList import MetaDataList
from lk_parks.metadata.MetaDataOriginalImage import MetaDataOriginalImage
from lk_parks.metadata.MetaDataREADME import MetaDataREADME


class MetaData(MetaDataBase, MetaDataBasePlantNet,
               MetaDataOriginalImage, MetaDataList, MetaDataREADME):
    pass
