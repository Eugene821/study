# RANSAC을 이용해 호모그래피 추정하기
import cv2
import numpy as np

img1=cv2.imread('mot_color70.jpg')[190:350,440:560] # 버스를 크롭하여 모델 영상으로 사용
gray1=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
img2=cv2.imread('mot_color83.jpg')			     # 장면 영상
gray2=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

sift=cv2.SIFT_create()
kp1,des1=sift.detectAndCompute(gray1,None)
kp2,des2=sift.detectAndCompute(gray2,None)

flann_matcher=cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
knn_match=flann_matcher.knnMatch(des1,des2,2)	# 최근접 2개

T=0.7
good_match=[]
for nearest1,nearest2 in knn_match:
    if (nearest1.distance/nearest2.distance)<T:
        good_match.append(nearest1)

# 영상의 특징점들의 좌표를 알아내 저장
points1=np.float32([kp1[gm.queryIdx].pt for gm in good_match])
points2=np.float32([kp2[gm.trainIdx].pt for gm in good_match])

# 호모그래피 행렬을 추정하여 H에 저장
H,_=cv2.findHomography(points1,points2,cv2.RANSAC)
# findHomography()
# 인수로 주어진 points1과 points2를 가지고, RANSAC 알고리즘 수행하여 호모그래피 행렬 추정

h1,w1=img1.shape[0],img1.shape[1] 		# 첫 번째 영상의 크기
h2,w2=img2.shape[0],img2.shape[1] 		# 두 번째 영상의 크기

# 네 구석의 좌표를 저장
box1=np.float32([[0,0],[0,h1-1],[w1-1,h1-1],[w1-1,0]]).reshape(4,1,2)
# 첫 번째 영상의 좌표에 호모그래피 행렬을 적용하여 두 번째 영상으로 투영하고 결과 저장
box2=cv2.perspectiveTransform(box1,H)

# polylines()로 box2 두 번째 영상에 그린다
img2=cv2.polylines(img2,[np.int32(box2)],True,(0,255,0),8)

img_match=np.empty((max(h1,h2),w1+w2,3),dtype=np.uint8)
cv2.drawMatches(img1,kp1,img2,kp2,good_match,img_match,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
   
cv2.imshow('Matches and Homography',img_match)

k=cv2.waitKey()
cv2.destroyAllWindows()