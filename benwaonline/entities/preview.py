from benwaonline.entities import Image

class Preview(Image):
    '''Represents a Preview resource object, related to the Preview model in the database

    Attributes:
        type_: 'previews'

    '''
    _schema = 'PreviewSchema'
    type_ = 'preview'
    attrs = {}

    