# Parking-bill-generator
Parking bill generator with image capturing feature deployed on AWS cloud.

### UseCase
- This is fully automated AI parking bill generator.
- Machine will capture image front view of car while entering mall.
- Machine will again capture car front view while exiting the mall.
- Machine will compute the parking bill based on the time the vehicle is parked in parking lot.

This is simple use case diagram describing how the parking bill generator works
![newb](https://github.com/user-attachments/assets/fcbed778-d9a0-4997-abe3-7ac6dc3cc781)

---

### Approach
- A simple UI with camera image capture option is created.
- Once if the user clicks on 'Click image' button. Image will be captured and added in AWS s3 bucket.
- When any image is uploaded in AWS s3 bucket, AWS lambda function will be invoked.
- AWS lambda takes the image from AWS s3 and push it AWS textract.
- AWS textract reads the image to extract text out of it. Vehicle number is extracted from the image.
- MySQL db is used to store the data.
