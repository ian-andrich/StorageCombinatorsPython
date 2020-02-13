### Storage Backend Test Images

If you are a developer wanting to run the integration test suite, you need docker-compose.

The images you need to build are contained in their respective folders.

#### Basic Operations

We expose up, stop and halt in the makefiles.  This provides a common interface for manipulating the images.

#### Ports exposed.
The ports exposed file details the exposed ports for each service, and will be used throughout the test suite.
