School Image Upload Feature

Some advice on creating a file upload interface in Vue:
https://blog.logrocket.com/customizing-drag-drop-file-uploading-vue/

This looks like a useful cropping script:
https://www.npmjs.com/package/react-image-crop

1. We need an interface that allows drag and drop.
2. Images can only be uploaded one at a time.
3. Each time the user selects an image, it is first validated in terms of file size and format.  Then they are presented with an interface that shows them how their image will be cropped (automatic default crop), and allows them to make adjustments.  We may need to upload the image to the uncropped bucket before we can do this.
4. Once the crop is confirmed, the image is cropped, then uploaded; the uncropped version to the uncropped bucket, if not already; and then the cropped version to the cropped bucket. 
5. The interface is closed, and a thumbnail of the image is shown, with options to delete or recrop.
6. Only one image is allowed for now, so no need to build a multi-image interface for now.  When the user reuses the interface, it simply replaces the current image.