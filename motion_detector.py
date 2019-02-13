from image_upload_config.tempimage import TempImage
from imutils.video import VideoStream
import argparse
import datetime
import dropbox
import imutils
import json
import time
import cv2
import warnings

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a","--min-area", type=int, default=500, help="minimum area size")
ap.add_argument("-c", "--config", required=True, help="path to the configuration file")
args = vars(ap.parse_args())

##filtre warnings
##Load the configuration from the Json file
warnings.filterwarnings("ignore")
conf = json.load(open(args["config"]))
client = None

##Creating environment depending on user inputs and configuration
if conf["use_dropbox"]:
    client = dropbox.Dropbox(conf["dropbox_access_token"])
    print("[SUCCESS] dropbox account linked")


if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
else :
    cv2.VideoCapture(args["Video"])

firstFrame = None

## Initialize some variables
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

while True:
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    timestamp = datetime.datetime.now()
    text = "Unoccupied"

    if frame is None:
        break

    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    ## Initialize firstFrame
    if firstFrame is None:
        firstFrame = gray
        continue
    
    ## Detect changes between the original weights of the pixels and the moving objects pixels
    ## delta = |background_model – current_frame|
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        continue
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv2.contourArea(c) < args["min_area"]:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

	# draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


    ## Upload occupied frame to DropBOX
    # check to see if the room is occupied
    if text == "Occupied":
	    # check to see if enough time has passed between uploads
        if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
            # increment the motion counter
            motionCounter += 1
			# check to see if the number of frames with consistent motion is high enough
            if motionCounter >= conf["min_motion_frames"]:
				# check to see if dropbox sohuld be used
                if conf["use_dropbox"]:
					# write the image to temporary file
                    t = TempImage()
                    cv2.imwrite(t.path, frame)

					# upload the image to Dropbox and cleanup the tempory image
                    print("[UPLOAD] {}".format(ts))
                    path = "/{base_path}/{timestamp}.jpg".format(base_path=conf["dropbox_base_path"], timestamp=ts)
                    client.files_upload(open(t.path, "rb").read(), path)
                    t.cleanup()

				# update the last uploaded timestamp and reset the motion
				# counter
                lastUploaded = timestamp
                motionCounter = 0

	# otherwise, the room is not occupied
    else:
        motionCounter = 0

    if conf["show_video"]:
        # show the frame and record if the user presses a key
        cv2.imshow("Home serveillance", frame)
        #cv2.imshow("Thresh", thresh)
        #cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()