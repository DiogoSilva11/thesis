# -----------------------------------------------------------------------------------------------------------------

class Applicant:
    def __init__(self, id : str) -> None:
        '''
        Initializes an user applying for a life insurance product
        '''
        self.id = id
        self.basic_info = []
        self.geo_indicators = []
        self.geo_index = None
        self.health_records = []
        self.health_index = None
        self.posts = []
        self.posts_index = None
        self.questions = []
        self.answers = {}
        self.reset_interactions()

    # -------------------------------------------------------------------------------------------------------------

    def reset_interactions(self) -> None:
        '''
        Resets variables storing data regarding agent interactions
        '''
        self.record = []

    # -------------------------------------------------------------------------------------------------------------

    def get_all_indices(self) -> dict:
        '''
        Returns all the FAISS indices stored
        '''
        indices = {}
        if self.geo_index:
            indices['geo'] = self.geo_index
        if self.health_index:
            indices['health'] = self.health_index
        if self.posts_index:
            indices['posts'] = self.posts_index
        return indices

    # -------------------------------------------------------------------------------------------------------------

    def get_all_data(self) -> dict:
        '''
        Returns all the data stored
        '''
        docs = {}
        if self.basic_info:
            docs['info'] = self.basic_info
        if self.geo_indicators:
            docs['geo'] = self.geo_indicators
        if self.health_records:
            docs['health'] = self.health_records
        if self.posts:
            docs['posts'] = self.posts
        return docs
    
    # -------------------------------------------------------------------------------------------------------------

    def to_json(self) -> dict:
        '''
        Returns the applicant as a JSON object
        '''
        return {
            'id': self.id,
            'basic_info': self.basic_info,
            'geo_indicators': self.geo_indicators,
            'health_records': self.health_records,
            'posts': self.posts
        }

# -----------------------------------------------------------------------------------------------------------------