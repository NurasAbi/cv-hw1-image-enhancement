| image        | method              |   PSNR |   SSIM |    MAE |
|:-------------|:--------------------|-------:|-------:|-------:|
| board1       | baseline            | 18.638 |  0.631 | 23.436 |
| board1       | stretch_lum         | 20.314 |  0.530 | 22.034 |
| board1       | hist_eq_lab         | 12.912 |  0.219 | 45.493 |
| board1       | stretch_nlm         | 20.674 |  0.939 | 22.173 |
| board1       | stretch_rgb (extra) | 20.196 |  0.443 | 21.441 |
| board2       | baseline            | 20.048 |  0.630 | 18.400 |
| board2       | stretch_lum         | 21.757 |  0.534 | 17.794 |
| board2       | hist_eq_lab         | 14.665 |  0.212 | 39.258 |
| board2       | stretch_nlm         | 22.267 |  0.935 | 17.665 |
| board2       | stretch_rgb (extra) | 22.055 |  0.438 | 16.339 |
| board3       | baseline            | 19.020 |  0.631 | 22.955 |
| board3       | stretch_lum         | 23.653 |  0.536 | 13.253 |
| board3       | hist_eq_lab         | 14.318 |  0.252 | 39.095 |
| board3       | stretch_nlm         | 24.714 |  0.930 | 11.612 |
| board3       | stretch_rgb (extra) | 22.602 |  0.458 | 15.217 |
| night_street | baseline            | 18.861 |  0.617 | 24.543 |
| night_street | stretch_lum         | 24.864 |  0.610 | 11.993 |
| night_street | hist_eq_lab         | 14.601 |  0.355 | 38.383 |
| night_street | stretch_nlm         | 25.959 |  0.826 | 10.628 |
| night_street | stretch_rgb (extra) | 24.517 |  0.498 | 12.248 |
| room_dark    | baseline            | 17.963 |  0.569 | 27.053 |
| room_dark    | stretch_lum         | 22.621 |  0.496 | 15.612 |
| room_dark    | hist_eq_lab         | 15.602 |  0.293 | 33.657 |
| room_dark    | stretch_nlm         | 23.572 |  0.862 | 14.019 |
| room_dark    | stretch_rgb (extra) | 21.656 |  0.391 | 17.482 |

Mean over images:

| method              |   PSNR |   SSIM |    MAE |
|:--------------------|-------:|-------:|-------:|
| baseline            | 18.906 |  0.616 | 23.277 |
| stretch_lum         | 22.642 |  0.541 | 16.137 |
| hist_eq_lab         | 14.420 |  0.266 | 39.177 |
| stretch_nlm         | 23.437 |  0.898 | 15.219 |
| stretch_rgb (extra) | 22.205 |  0.446 | 16.545 |
