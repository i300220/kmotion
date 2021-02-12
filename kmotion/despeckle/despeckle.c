#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jpeglib.h>
#include <setjmp.h>


#define MAX(x, y) (abs(x) > abs(y) ? (x) : (y))

/* Dilates a 3x3 box */
static int dilate9(char *img, int width, int height, void *buffer)
{
	int y, i, sum = 0;
	char *Row1,*Row2,*Row3;
	Row1 = buffer;
	Row2 = Row1 + width;
	Row3 = Row1 + 2*width;
	memset(Row2, 0, width);
	memcpy(Row3, img, width);
	for (y = 0; y < height; y++) {
		memcpy(Row1, Row2, width);
		memcpy(Row2, Row3, width);
		if (y == height-1)
			memset(Row3, 0, width);
		else
			memcpy(Row3, img+(y+1)*width, width);

		for (i = width-2; i >= 1; i--) {
		  int blob;
		  blob = MAX(Row1[i-1], Row1[i]);
		  blob = MAX(blob, Row1[i+1]);
		  blob = MAX(blob, Row2[i-1]);
		  blob = MAX(blob, Row2[i]);
		  blob = MAX(blob, Row2[i+1]);
		  blob = MAX(blob, Row3[i-1]);
		  blob = MAX(blob, Row3[i]);
		  blob = MAX(blob, Row3[i+1]);
		  if (blob != 0) {
		    img[y*width+i] = blob;
		    sum++;
		  }
		}
		img[y*width] = img[y*width+width-1] = 0;
	}
	return sum;
}


/* Dilates a + shape */
static int dilate5(char *img, int width, int height, void *buffer)
{
	int y, i, sum = 0;
	char *Row1,*Row2,*Row3;
	Row1 = buffer;
	Row2 = Row1 + width;
	Row3 = Row1 + 2*width;
	memset(Row2, 0, width);
	memcpy(Row3, img, width);
	for (y = 0; y < height; y++) {
		memcpy(Row1, Row2, width);
		memcpy(Row2, Row3, width);
		if (y == height-1)
			memset(Row3, 0, width);
		else
			memcpy(Row3, img+(y+1)*width, width);

		for (i = width-2; i >= 1; i--) {
		  int blob;
		  blob = MAX(Row1[i], Row2[i-1]);
		  blob = MAX(blob, Row2[i]);
		  blob = MAX(blob, Row2[i+1]);
		  blob = MAX(blob, Row3[i]);
		  if (blob != 0) {
		    img[y*width+i] = blob;
		    sum++;
		  }
		}
		img[y*width] = img[y*width+width-1] = 0;
	}
	return sum;
}


/* Erodes a 3x3 box */
static int erode9(char *img, int width, int height, void *buffer)
{
	int y, i, sum = 0;
	char *Row1,*Row2,*Row3;
	Row1 = buffer;
	Row2 = Row1 + width;
	Row3 = Row1 + 2*width;
	memset(Row2, 0, width);
	memcpy(Row3, img, width);
	for (y = 0; y < height; y++) {
		memcpy(Row1, Row2, width);
		memcpy(Row2, Row3, width);
		if (y == height-1)
			memset(Row3, 0, width);
		else
			memcpy(Row3, img+(y+1)*width, width);

		for (i = width-2; i >= 1; i--) {
			if (Row1[i-1] == 0 ||
			    Row1[i]   == 0 ||
			    Row1[i+1] == 0 ||
			    Row2[i-1] == 0 ||
			    Row2[i]   == 0 ||
			    Row2[i+1] == 0 ||
			    Row3[i-1] == 0 ||
			    Row3[i]   == 0 ||
			    Row3[i+1] == 0)
			  img[y*width+i] = 0;
			else
			  sum++;
		}
		img[y*width] = img[y*width+width-1] = 0;
	}
	return sum;
}

/* Erodes in a + shape */
static int erode5(char *img, int width, int height, void *buffer)
{
	int y, i, sum = 0;
	char *Row1,*Row2,*Row3;
	Row1 = buffer;
	Row2 = Row1 + width;
	Row3 = Row1 + 2*width;
	memset(Row2, 0, width);
	memcpy(Row3, img, width);
	for (y = 0; y < height; y++) {
		memcpy(Row1, Row2, width);
		memcpy(Row2, Row3, width);
		if (y == height-1)
			memset(Row3, 0, width);
		else
			memcpy(Row3, img+(y+1)*width, width);

		for (i = width-2; i >= 1; i--) {
			if (Row1[i]   == 0 ||
			    Row2[i-1] == 0 ||
			    Row2[i]   == 0 ||
			    Row2[i+1] == 0 ||
			    Row3[i]   == 0)
			  img[y*width+i] = 0;
			else
			  sum++;
		}
		img[y*width] = img[y*width+width-1] = 0;
	}
	return sum;
}


static void print_mat(char *img, int width, int height)
{
  int across, down, size = 10;
  (void)height;
  printf("\n"); // img[4*width+10] = img[4*width+11] = 1;
  for (down = 0; down < size; down++) {
    for (across = 0; across < 40; across++)
      printf("%02X", img[down*width+across]);
    printf("\n");
  }
}


/* 
 * Despeckling routine to remove noisy detections.
 */
#undef YUVDESPECKLE
int alg_despeckle(char *out, int width, int height, char *despeckle)
{
	int diffs = 0;
	int i, len = strlen(despeckle);
	void *buffer = malloc(3*width);

        if (!buffer) return 0;

	for (i = 0; i < len; i++) {
		switch (despeckle[i]) {
		case 'E':
			diffs = erode9(out, width, height, buffer);
#ifdef YUVDESPECKLE
			diffs += erode9(out+width*height, width, height, buffer);
			diffs += erode9(out+2*width*height, width/2, height/2, buffer);
#endif
			break;
		case 'e':
			diffs = erode5(out, width, height, buffer);
#ifdef YUVDESPECKLE
			diffs += erode5(out+width*height, width, height, buffer);
			diffs += erode5(out+2*width*height, width/2, height/2, buffer);
#endif
			break;
		case 'D':
			diffs = dilate9(out, width, height, buffer);
#ifdef YUVDESPECKLE
			diffs += dilate9(out+width*height, width, height, buffer);
			diffs += dilate9(out+2*width*height, width/2, height/2, buffer);
#endif
			break;
		case 'd':
			diffs = dilate5(out, width, height, buffer);
#ifdef YUVDESPECKLE
			diffs += dilate5(out+width*height, width, height, buffer);
			diffs += dilate5(out+2*width*height, width/2, height/2, buffer);
#endif
			break;
		case 'I':
		case 'i':
			print_mat(out, width, height);
			break;
		}
	}
        free(buffer);
	return diffs;
}



void put_jpeg_yuv420p (FILE *fp, unsigned char *image, int width, int height, int quality)
{
	int i,j;

	JSAMPROW y[16],cb[16],cr[16]; // y[2][5] = color sample of row 2 and pixel column 5; (one plane)
	JSAMPARRAY data[3]; // t[0][2][5] = color sample 0 of row 2 and column 5

	struct jpeg_compress_struct cinfo;
	struct jpeg_error_mgr jerr;

	data[0] = y;
	data[1] = cb;
	data[2] = cr;

	cinfo.err = jpeg_std_error(&jerr);  // errors get written to stderr 
	
	jpeg_create_compress (&cinfo);
	cinfo.image_width = width;
	cinfo.image_height = height;
	cinfo.input_components = 3;
	jpeg_set_defaults (&cinfo);

	jpeg_set_colorspace(&cinfo, JCS_YCbCr);

	cinfo.raw_data_in = TRUE; // supply downsampled data
	cinfo.comp_info[0].h_samp_factor = 2;
	cinfo.comp_info[0].v_samp_factor = 2;
	cinfo.comp_info[1].h_samp_factor = 1;
	cinfo.comp_info[1].v_samp_factor = 1;
	cinfo.comp_info[2].h_samp_factor = 1;
	cinfo.comp_info[2].v_samp_factor = 1;

	jpeg_set_quality (&cinfo, quality, TRUE);
	cinfo.dct_method = JDCT_FASTEST;

	jpeg_stdio_dest (&cinfo, fp);  	  // data written to file
	jpeg_start_compress (&cinfo, TRUE);
  
	for (j=0;j<height;j+=16) {
		for (i=0;i<16;i++) {
			y[i] = image + width*(i+j);
			if (i%2 == 0) {
				cb[i/2] = image + width*height + width/2*((i+j)/2);
				cr[i/2] = image + width*height + width*height/4 + width/2*((i+j)/2);
			}
		}
		jpeg_write_raw_data (&cinfo, data, 16);
  	}

	jpeg_finish_compress (&cinfo);
	jpeg_destroy_compress (&cinfo);
}

struct my_error_mgr {
  struct jpeg_error_mgr pub;	/* "public" fields */

  jmp_buf setjmp_buffer;	/* for return to caller */
};

typedef struct my_error_mgr * my_error_ptr;

static void my_error_exit (j_common_ptr cinfo)
{
  my_error_ptr myerr = (my_error_ptr) cinfo->err;
  (*cinfo->err->output_message) (cinfo);
  longjmp(myerr->setjmp_buffer, 1);
}


static char *read_JPEG_file(char *filename, int *jpegwidth, int *jpegheight)
{
  struct jpeg_decompress_struct cinfo;
  struct my_error_mgr jerr;
  FILE * infile;		/* source file */
  JSAMPARRAY line;
  JSAMPROW row[1];
  int width, height, y, i, line_size;
  char *pic, *result, *upic, *vpic;

  if ((infile = fopen(filename, "rb")) == NULL) {
    fprintf(stderr, "can't open %s\n", filename);
    return 0;
  }

  cinfo.err = jpeg_std_error(&jerr.pub);
  jerr.pub.error_exit = my_error_exit;
  if (setjmp(jerr.setjmp_buffer)) {
    jpeg_destroy_decompress(&cinfo);
    fclose(infile);
    return 0;
  }

  jpeg_create_decompress(&cinfo);
  jpeg_stdio_src(&cinfo, infile);
  (void) jpeg_read_header(&cinfo, TRUE);

  cinfo.out_color_space=JCS_YCbCr;
	
  jpeg_start_decompress(&cinfo);
  width = cinfo.image_width;
  height = cinfo.image_height;
  line_size = width * 3;
	
  line = (*cinfo.mem->alloc_sarray) ((j_common_ptr) &cinfo, JPOOL_IMAGE, cinfo.output_width*cinfo.output_components, 1);
  pic = result = malloc(3 * width * height);
  upic = pic + (width * height);
  vpic = upic + (width*height)/4;
  row[0]=(unsigned char *)line;
  y=0;
  while (cinfo.output_scanline < (unsigned int)height) {
    jpeg_read_scanlines(&cinfo, row, 1);
    for (i = 0; i < line_size; i += 3) {
      pic[i/3]=((unsigned char *)line)[i];
      if (i & 1) {
        upic[(i/3)/2]=((unsigned char *)line)[i+1];
        vpic[(i/3)/2]=((unsigned char *)line)[i+2];
      }
    }
    pic += line_size/3;
    if (y++ & 1) {
      upic += width / 2;
      vpic += width / 2;
    }
  }
  jpeg_finish_decompress(&cinfo);
  jpeg_destroy_decompress(&cinfo);
  fclose(infile);

  *jpegwidth = width;
  *jpegheight = height;
  return result;
}


int main(int nargs, char *argv[])
{
  char *despeckle, *infile, *outfile;
  char *image;
  int width, height;

  if (nargs != 4) {
    printf("Usage %s EedD infile.jpg outfile.jpg\n", argv[0]);
    exit(1);
  }
  despeckle = argv[1];
  infile = argv[2];
  outfile = argv[3];

  image = read_JPEG_file(infile, &width, &height);
  alg_despeckle(image, width, height, despeckle);

  { FILE *fp;
  fp = fopen(outfile, "wb");
  put_jpeg_yuv420p(fp, image, width, height, 90);
  fclose(fp);
  }

  return 0;
}
