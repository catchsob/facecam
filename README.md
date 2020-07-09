# facecam
A face recognition application on variant platform

facegen.py to generate a face encoding csv file
1. prepare jpg face image files with labeled file name (such as chou.jpg, wang.jpg, ... etc) in specific directory (such as train)
2. generate the face encoding file by command "python3 facegen.py -p train"
"python3 facegen.py --help" to get usage

facecam.py to recognize the face by cam (realtime) or picture (batch)
1. prepare jpg face image files (001.jpg) in specific directory (such as test)
2. recognize the image file by command "python3 facecam.py -p test/001.jpg"
3. if Pi Camera is installed, you may run realtime face recognition by command "python3 facecam.py"
"python3 facecam.py --help" to get usage

supported platform: Microsoft Windows 10/ NVIDIA Jetson Nano/ Raspberry Pi 3B+

necessary library: dlib, pillow, opencv, numpy, face_recognition

note: TaipeiSansTCBeta-Regular.ttf is an open true type font in Chinese from https://sites.google.com/view/jtfoundry/en for running the code on Respberry Pi. You should adopt it by "-f TaipeiSansTCBeta-Regular.ttf" once your label is in Chinese and command "python3 facecam.py".
