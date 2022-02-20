test_config = {
'path': 'photo/original/',
'CARD_ID': '0',
'model': './weights_rects/east_200_2378.pth',
'outputs': 'photo/processed/',
#'test_size': (768, 1280),
'test_size': (480, 480),
'nms_thres': 0.2,
'reselect_thres': 0.2
}
