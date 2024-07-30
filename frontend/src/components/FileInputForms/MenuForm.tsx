import {
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  HStack,
  Image,
  Link,
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
import { getEateryDetails, updateEateryMenu } from '../../utils/api/eateries';
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';

registerPlugin(
  FilePondPluginFileEncode,
  FilePondPluginImageExifOrientation,
  FilePondPluginImagePreview,
  FilePondPluginFileValidateType
);

type MenuFormProps = {
  submitted: () => void;
};

const MenuForm = forwardRef<HTMLButtonElement, MenuFormProps>((props, ref) => {
  const { getters } = useContext(AuthContext);
  const queryClient = useQueryClient();
  const filePondRef = React.useRef<FilePond>(null);

  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState('');

  const [menu, setMenu] = useState<string>();
  const [showFileUpload, setShowFileUpload] = useState<boolean>(false);

  const { mutate } = useMutation({
    mutationFn: (menu_uri: string) =>
      updateEateryMenu(getters.sessionToken!, getters.userId!, menu_uri),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['eatery', getters.userId]
      });

      // Reset form state
      setIsSubmitting(false);
      setFiles([]);

      props.submitted();
    }
  });

  useEffect(() => {
    // Fetch eatery details when the component mounts
    const fetchData = async () => {
      try {
        const details = await getEateryDetails(
          getters.sessionToken!,
          getters.userId!
        );
        // TODO: change condition when menu_upcoming_soon.jpg is redacted
        if (details.menu_uri !== './menu_upcoming_soon.jpg') {
          setMenu(details.menu_uri);
        }
        console.log(details);
      } catch (error) {
        console.error('Error fetching eatery details:', error);
        setError('Error fetching eatery details');
      }
    };
    fetchData();
  }, [getters.sessionToken, getters.userId]);

  // Clear/add error message when files are uploaded
  useEffect(() => {
    for (const file of files) {
      if (file.type !== 'application/pdf') {
        setError('Please upload a pdf file.');
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
      //   setError('Please upload a pdf for your menu.');
      //   return;
      // }
      if (error) {
        return;
      }
      setIsSubmitting(true);

      const pdfURI = filePondRef.current?.getFiles()[0].getFileEncodeDataURL();

      console.log('menu submitting');

      mutate(pdfURI!);
    }
  };

  return (
    <>
      <chakra.form
        onSubmit={handleSubmit}
        display="flex"
        flexDirection="column"
        alignItems="center"
        width="100%">
        <HStack
          justifyContent="space-between"
          width="100%"
          bgColor="chowdownPurple.50"
          padding="3"
          borderRadius="md">
          <HStack>
            {menu ? (
              <>
                <Image
                  boxSize="10"
                  src="https://cdn-icons-png.flaticon.com/512/4813/4813396.png"
                />
                <Link
                  href={menu}
                  download="menu.pdf"
                  rel="noopener noreferrer"
                  isExternal
                  color="chowdownPurple.500">
                  menu.pdf
                </Link>
              </>
            ) : (
              <Box marginLeft={3}>Upload new menu</Box>
            )}
          </HStack>
          <Box>
            <Button onClick={() => setShowFileUpload(true)}>Update</Button>
          </Box>
        </HStack>
        {showFileUpload && (
          <FormControl isInvalid={!!error}>
            <FilePond
              ref={filePondRef}
              files={files}
              onupdatefiles={(fileItems) => {
                setFiles(fileItems.map((fileItem) => fileItem.file as File));
              }}
              acceptedFileTypes={['application/pdf']}
              labelFileTypeNotAllowed="Please upload a pdf file."
              fileValidateTypeLabelExpectedTypes="Expects {allTypes}"
              name="menu"
              credits={false}
            />
            <FormErrorMessage>{error}</FormErrorMessage>
            <Button
              style={{ display: 'none' }}
              type="submit"
              isLoading={isSubmitting}
              ref={ref}>
              Save
            </Button>
          </FormControl>
        )}
      </chakra.form>
    </>
  );
});

MenuForm.displayName = 'MenuForm';

export default MenuForm;
