import { ReactNode, useRef, useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Icon,
  Image,
  InputGroup,
  Link
} from '@chakra-ui/react';
import { useForm, UseFormRegisterReturn } from 'react-hook-form';
import { AttachmentIcon } from '@chakra-ui/icons';

type FileUploadProps = {
  register: UseFormRegisterReturn;
  accept?: string;
  multiple?: boolean;
  children?: ReactNode;
};

const FileUpload = (props: FileUploadProps) => {
  const { register, accept, multiple, children } = props;
  const inputRef = useRef<HTMLInputElement | null>(null);
  const { ref, ...rest } = register as {
    ref: (instance: HTMLInputElement | null) => void;
  };

  const handleClick = () => inputRef.current?.click();

  return (
    <InputGroup onClick={handleClick}>
      <input
        type={'file'}
        multiple={multiple || false}
        hidden
        accept={accept}
        {...rest}
        ref={(e) => {
          ref(e);
          inputRef.current = e;
        }}
      />
      <>{children}</>
    </InputGroup>
  );
};

type FormValues = {
  file_: FileList;
};

const fileToDataUrl = async (file: File): Promise<string> => {
  const validFileTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  const valid = validFileTypes.find((type) => type === file.type);
  // Bad data, let's walk away.
  if (!valid) {
    throw Error('provided file is not a png, jpg or jpeg image.');
  }

  const dataUrlPromise = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = () => resolve(reader.result as string);
    reader.readAsDataURL(file);
  });
  return dataUrlPromise;
};

const UploadFile = () => {
  const [fileName, setFileName] = useState<string>('');
  const [dataUrl, setDataUrl] = useState<string>('');
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<FormValues>();
  const onSubmit = handleSubmit(async (data) => {
    const uploadedFiles = data.file_;
    const file = uploadedFiles[0];
    if (file) {
      setFileName(file.name);
    }
    console.log('On Submit: ', data);
    const dataUrl = await fileToDataUrl(file);
    setDataUrl(dataUrl);
  });

  const validateFiles = (value: FileList) => {
    if (value.length < 1) {
      return 'Please select a file';
    }
    for (const file of Array.from(value)) {
      const fsMb = file.size / (1024 * 1024);
      const MAX_FILE_SIZE = 10;
      if (fsMb > MAX_FILE_SIZE) {
        return 'Max file size 10mb';
      }
    }
    return true;
  };

  return (
    <>
      <Box width="100%">
        <form onChange={onSubmit}>
          <FormControl isInvalid={!!errors.file_} isRequired>
            <FormLabel>{'File input'}</FormLabel>
            <HStack
              justifyContent="space-between"
              width="100%"
              bgColor="chowdownPurple.50"
              padding="3">
              <HStack>
                {fileName ? (
                  <>
                    <Image
                      boxSize="10"
                      src="https://cdn-icons-png.flaticon.com/512/4813/4813396.png"
                    />
                    <Link
                      href={dataUrl}
                      download={fileName}
                      rel="noopener noreferrer"
                      isExternal
                      color="chowdownPurple.500">
                      {fileName}
                    </Link>
                  </>
                ) : (
                  <Box marginLeft={3}>Nothing yet</Box>
                )}
              </HStack>
              <Box>
                <FileUpload
                  accept={'image/*'}
                  register={register('file_', { validate: validateFiles })}>
                  <Button leftIcon={<Icon as={AttachmentIcon} />}>
                    Replace
                  </Button>
                </FileUpload>
              </Box>
            </HStack>
            <FormErrorMessage>
              {errors.file_ && errors?.file_.message}
            </FormErrorMessage>
          </FormControl>
        </form>
      </Box>
    </>
  );
};

export default UploadFile;
