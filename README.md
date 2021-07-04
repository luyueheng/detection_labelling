# Image Labelling Tool for Computer Vision Tasks

An interactive web application designed for labelling images and storing results to cloud database. As a demonstration, currently the server is connected to a MySQL database on AWS RDS.

The server is written with Flask framework. The annotations on top of image is achieved by Fabric.js. The input of object category supports typeahead.

### Features

1. Label meta data of an image
2. Annotate image with bounding boxes of objects and enter object category for each box
3. Quick view of labelling results without updating database
4. Document batch job description, labeller and labelling time
5. Quit before this batch is done and automatically save unfinished image id in .txt



