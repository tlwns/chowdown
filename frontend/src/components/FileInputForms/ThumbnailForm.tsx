import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  chakra
} from '@chakra-ui/react';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import FilePondPluginFileEncode from 'filepond-plugin-file-encode';
import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation';
import FilePondPluginImagePreview from 'filepond-plugin-image-preview';
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css';
import 'filepond/dist/filepond.min.css';
import React, { forwardRef, useContext, useEffect, useState } from 'react';
import { FilePond, registerPlugin } from 'react-filepond';
import { AuthContext } from '../../context/authContext';
import { updateEateryThumbnail } from '../../utils/api/eateries';
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';

registerPlugin(
  FilePondPluginFileEncode,
  FilePondPluginImageExifOrientation,
  FilePondPluginImagePreview,
  FilePondPluginFileValidateType
);

type ThumbnailFormProps = {
  submitted: () => void;
};

const ThumbnailForm = forwardRef<HTMLButtonElement, ThumbnailFormProps>(
  (props, ref) => {
    const { getters } = useContext(AuthContext);
    const queryClient = useQueryClient();
    const filePondRef = React.useRef<FilePond>(null);

    const [files, setFiles] = useState<File[]>([]);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState('');

    const { mutate } = useMutation({
      mutationFn: (thumbnail_uri: string) =>
        updateEateryThumbnail(
          getters.sessionToken!,
          getters.userId!,
          thumbnail_uri
        ),
      onSuccess: () => {
        console.log('successfully updated thumbnail');
        queryClient.invalidateQueries({
          queryKey: ['eatery', getters.userId]
        });

        // Reset form state
        setIsSubmitting(false);
        setFiles([]);

        props.submitted();
      }
    });

    // Clear/add error message when files are uploaded
    useEffect(() => {
      for (const file of files) {
        if (file.type !== 'image/jpeg' && file.type !== 'image/png') {
          setError('Please upload an image file.');
          return;
        }
      }

      if (files.length > 0) {
        setError('');
      }
    }, [files]);

    // Handle form submission
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (files.length !== 0) {
        if (error) {
          return;
        }
        setIsSubmitting(true);

        const thumbnailURI = filePondRef.current
          ?.getFiles()[0]
          .getFileEncodeDataURL();

        mutate(thumbnailURI!);
      }
    };

    return (
      <>
        <chakra.form
          onSubmit={handleSubmit}
          display="flex"
          flexDirection="column"
          alignItems="center"
          width="100%"
          flex={1}>
          <FormControl isRequired isInvalid={!!error} className="thumbnail">
            <FormLabel>Thumbnail</FormLabel>
            <FilePond
              ref={filePondRef}
              files={files}
              onupdatefiles={(fileItems) => {
                setFiles(fileItems.map((fileItem) => fileItem.file as File));
              }}
              acceptedFileTypes={['image/*']}
              labelFileTypeNotAllowed="Please upload an image file."
              fileValidateTypeLabelExpectedTypes="Expects {allTypes}"
              name="thumbnail"
              credits={false}
            />
            <FormErrorMessage>{error}</FormErrorMessage>
          </FormControl>

          <Button
            style={{ display: 'none' }}
            type="submit"
            isLoading={isSubmitting}
            ref={ref}>
            Save
          </Button>
        </chakra.form>
      </>
    );
  }
);

ThumbnailForm.displayName = 'ThumbnailForm';

export default ThumbnailForm;
