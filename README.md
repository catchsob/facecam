# facecam
A face recognition suite on variant platform

### fagen.py

to generate a face encoding csv file
1. prepare jpg face image files with labeled file name (such as chou.jpg, wang.jpg, ... etc) in specific directory (such as train)
2. generate the face encoding file by command "python3 facegen.py -p train"
3. "python3 facegen.py --help" to get usage

### faceme.py

to register a face via cam picturing

1. a camera on Windows or Pi Camera on Jetson Nano/ Raspberry Pi is necessary.
2. start the face picturing and registering by command "python3 faceme.py"
3. "python3 faceme.py --help" to get usage

### facecam.py

to recognize the face by cam (realtime) or picture (batch)

1. prepare jpg face image files (such as 001.jpg) in specific directory (such as test)
2. recognize the image file by command "python3 facecam.py -p test/001.jpg"
3. if camera on Windows or Pi Camera is installed on Jetson Nano/ Raspberry Pi, you may run realtime face recognition by command "python3 facecam.py"
4. "python3 facecam.py --help" to get usage

##### platforms

Microsoft Windows 10/ NVIDIA Jetson Nano/ Raspberry Pi 3B+

##### dependencies

dlib, pillow, opencv (facecam, faceme), numpy, face_recognition, python3-tk (faceme)

##### notes

TaipeiSansTCBeta-Regular.ttf is an open true type font in Chinese from https://sites.google.com/view/jtfoundry/en for running the code on Respberry Pi. You should adopt it by "-f TaipeiSansTCBeta-Regular.ttf" once your label is in Chinese and command "python3 facecam.py".
