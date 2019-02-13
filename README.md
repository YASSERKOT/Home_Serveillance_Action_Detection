# Home_Serveillance_Action_Detection
```
Created for "KOTRSI EVENT PLANNING STORE"
```
# Project schema :
```
|--- motion_detector.py : contains all the script logic.
```
|--- conf.json : contains the configuration of the project, you can add you DropBox store application token in it.
```
|--- image_upload_config
```
|    |--- __init__.py
```
|    |--- tempimage.py : script that handles the uploading of images toward your specified directory on DropBox.
```
You can run the script by running : # python motion_detector.py --config conf.json
```
# The Conf.Json configuration is detailed below :
```
    show_video : A boolean indicating whether or not the video stream from the Raspberry Pi should be displayed to our screen.
    ```
    use_dropbox : Boolean indicating whether or not the Dropbox API integration should be used.
    ```
    dropbox_access_token : Your public Dropbox API key.
    ```
    dropbox_base_path : The name of your Dropbox App directory that will store uploaded images.
    ```
    min_upload_seconds : The number of seconds to wait in between uploads. For example, if an image was uploaded to Dropbox 5m 33s after starting our script, a second image would not be uploaded until 5m 36s. This parameter simply controls the frequency of image uploads.
    ```
    min_motion_frames : The minimum number of consecutive frames containing motion before an image can be uploaded to Dropbox.
    ```
    camera_warmup_time : The number of seconds to allow the Raspberry Pi camera module to “warmup” and calibrate.
    ```
    delta_thresh : The minimum absolute value difference between our current frame and averaged frame for a given pixel to be “triggered” as motion. Smaller values will lead to more motion being detected, larger values to less motion detected.
    ```
    resolution : The width and height of the video frame from our Raspberry Pi camera.
    ```
    fps : The desired Frames Per Second from our Raspberry Pi camera.
    ```
    min_area : The minimum area size of an image (in pixels) for a region to be considered motion or not. Smaller values will lead to more areas marked as motion, whereas higher values of min_area  will only mark larger regions as motion.
