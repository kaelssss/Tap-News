import json

MACHINE_LEARNING_PARAM = {
    'topic_modeling': {
        'number_classes': 10,
        'training_index_end': 1400,
        'testing_index_end': 100,
        'max_document_length': 500,
        'min_frequency': 50,
        'steps': 50,
        'learning_rate': 0.03,
        'embedding_size': 40,
        'number_filters': 10,
        'window_size': 20,
        'pooling_window': 4,
        'pooling_stride': 2
    }
}

def getMachineLearningParamForUsecase(usecase_name):
    return getParamForUsecase(usecase_name, MACHINE_LEARNING_PARAM)

def getParamForUsecase(usecase_name, params_name):
    param = {}
    if usecase_name in params_name:
        param = params_name[usecase_name]
    print param
    return json.dumps(param)