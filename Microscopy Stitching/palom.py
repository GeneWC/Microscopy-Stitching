import palom

# reference image is a multichannel immunofluoroscence imaging
c1r = palom.reader.OmePyramidReader(r"C:\Users\zionc\Downloads\Bone5 Met1 1.ome-002.tiff")
# moving image is a brightfield imaging (H&E staining) of the same tissue
# section as the reference image
c2r = palom.reader.OmePyramidReader(r"C:\Users\zionc\Downloads\Image_Bone5 Met1 2 Her2-003.btf")

# use second-to-the-bottom pyramid level for a quick test; set `LEVEL = 0` for
# processing lowest level pyramid (full resolution)
LEVEL = 1
# choose thumbnail pyramid level for feature-based affine registration as
# initial coarse alignment
# `THUMBNAIL_LEVEL = c1r.get_thumbnail_level_of_size(2000)` might be a good
# starting point
THUMBNAIL_LEVEL = 3

c21l = palom.align.Aligner(
    # use the first channel (Hoechst staining) in the reference image as the
    # registration reference
    ref_img=c1r.read_level_channels(LEVEL, 0),
    # use the second channel (G channel) in the moving image, it usually has
    # better contrast
    moving_img=c2r.read_level_channels(LEVEL, 1),
    # select the same channels for the thumbnail images
    ref_thumbnail=c1r.read_level_channels(THUMBNAIL_LEVEL, 0).compute(),
    moving_thumbnail=c2r.read_level_channels(THUMBNAIL_LEVEL, 1).compute(),
    # specify the downsizing factors so that the affine matrix can be scaled to
    # match the registration reference
    ref_thumbnail_down_factor=c1r.level_downsamples[THUMBNAIL_LEVEL] / c1r.level_downsamples[LEVEL],
    moving_thumbnail_down_factor=c2r.level_downsamples[THUMBNAIL_LEVEL] / c2r.level_downsamples[LEVEL]
)

# run feature-based affine registration using thumbnails
c21l.coarse_register_affine(n_keypoints=4000)
# after coarsly affine registered, run phase correlation on each of the
# corresponding chunks (blocks/pieces) to refine translations
c21l.compute_shifts()
# discard incorrect shifts which is usually due to low contrast in the
# background regions; this is needed for WSI but maybe not for ROI images
c21l.constrain_shifts()

# configure the transformation of aligning the moving image to the registration
# reference
c2m = palom.align.block_affine_transformed_moving_img(
    ref_img=c1r.read_level_channels(LEVEL, 0),
    # select all the three channels (RGB) in moving image to transform
    moving_img=c2r.pyramid[LEVEL],
    mxs=c21l.block_affine_matrices_da
)

# write the registered images to a pyramidal ome-tiff
palom.pyramid.write_pyramid(
    mosaics=[
        # select only the first three channels in referece image to be written
        # to the output ome-tiff; for writing all channels, use
        # `c1r.pyramid[LEVEL]` instead
        c1r.read_level_channels(LEVEL, [0, 1, 2]),
        c2m
    ],
    output_path=r"Z:\P37_Pilot2\mosaic.ome.tif",
    pixel_size=c1r.pixel_size*c1r.level_downsamples[LEVEL]
)


