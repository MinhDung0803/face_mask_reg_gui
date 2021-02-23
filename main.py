import app_test
import face_mask_detection
import sys
import json
import yaml
import warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":
    abc = 123
    app_test.app_threading(abc)
    print("xxxdsdsdsdsdsdsdsdsdddddddddddddddddddddddddddddddddddddddddddddddd")

    if len(sys.argv) < 2:
        print(
            "------------------------------------------------------------------------------------\n"
            "Call this program like this:\n\n"
            "python  ./face_recognition_demo.py path_to_config_file.yml"
            "\n"
            )

        exit()

    print('\n--------------------------------- Face Recognition System ---------------------------------\n\n')

    print("S keypress: Change small size view <-> original size view")
    print("P keypress: Pause")
    print("Q or Esc keypress: Quit")
    print('\n\n-----------------------------------------------------------------------------------\n')

    config_file = sys.argv[1]

    face_mask_detection.reading_test_by_threading(config_file)

    # print("xxxdsdsdsdsdsdsdsdsdddddddddddddddddddddddddddddddddddddddddddddddd")
    # abc = 123
    # app_test.app_threading(abc)
