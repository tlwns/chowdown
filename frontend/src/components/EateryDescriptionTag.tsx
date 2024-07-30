import { forwardRef, useContext, useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  HStack,
  Heading,
  Input,
  InputGroup,
  InputLeftElement,
  Tag,
  TagCloseButton,
  TagLabel,
  Text,
  Textarea
} from '@chakra-ui/react';
import { AuthContext } from '../context/authContext';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getEateryDetails, updateEateryDetails } from '../utils/api/eateries';
import { Form } from 'react-router-dom';
import { AddIcon, EditIcon } from '@chakra-ui/icons';

type DescriptionTagFormProps = {
  submitted: () => void;
};

const EateryDescriptionTag = forwardRef<
  HTMLButtonElement,
  DescriptionTagFormProps
>((props, ref) => {
  const { getters } = useContext(AuthContext);
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const [isEditing, setIsEditing] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState('');

  const [updatedFields, setUpdatedFields] =
    useState<EateryUpdateDetailsRequest>({});

  const { data } = useQuery({
    queryKey: ['eatery', getters.userId!, 'details'],
    queryFn: async () => {
      try {
        const details = await getEateryDetails(
          getters.sessionToken!,
          getters.userId!
        );
        return details;
      } catch (error) {
        console.error('Error fetching eatery details:', error);
        setError('Error fetching eatery details');
        return null;
      }
    },
    enabled: !!getters.userId
  });

  const { mutate } = useMutation({
    mutationFn: (updatedData: EateryUpdateDetailsRequest) =>
      updateEateryDetails(getters.sessionToken!, getters.userId!, updatedData),
    onSuccess: () => {
      console.log('successfully updated description');
      queryClient.invalidateQueries({
        queryKey: ['eatery', getters.userId]
      });
      setIsSubmitting(false);
      props.submitted();
    }
  });

  const handleFieldChange = (fieldName: string, value: string | string[]) => {
    setUpdatedFields((prevState) => ({
      ...prevState,
      [fieldName]: value
    }));
  };

  const handleSubmit = () => {
    if (error) {
      return;
    }
    mutate(updatedFields);
  };

  const handleKeywordInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const newKeyword = e.currentTarget.value.trim();
      if (newKeyword) {
        setUpdatedFields((prevFields) => ({
          ...prevFields,
          keywords: [
            ...(prevFields.keywords ?? (data?.keywords || [])),
            newKeyword
          ]
        }));
        e.currentTarget.value = '';
      }
    }
  };

  const handleRemoveKeyword = (indexToRemove: number) => {
    setUpdatedFields((prevFields) => ({
      ...prevFields,
      keywords: (prevFields.keywords ?? (data?.keywords || [])).filter(
        (_, index) => index !== indexToRemove
      )
    }));
  };

  return (
    <>
      <Heading size="md">Description</Heading>
      <FormControl>
        <Form onSubmit={handleSubmit}>
          {isEditing.description ? (
            <Textarea
              value={updatedFields.description ?? data?.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              onBlur={(e) => {
                handleFieldChange('description', e.target.value);
                setIsEditing((prevState) => ({
                  ...prevState,
                  description: false
                }));
              }}
              placeholder="Edit Description"
            />
          ) : (
            <HStack width="100%" justifyContent="space-between" align="top">
              <Box>
                {data?.description !== '' ? (
                  updatedFields.description !== undefined ? (
                    updatedFields.description
                  ) : (
                    data?.description
                  )
                ) : (
                  <Text flexWrap="wrap">No description yet...</Text>
                )}
              </Box>
              <Button
                onClick={() => {
                  setIsEditing((prevState) => ({
                    ...prevState,
                    description: true
                  }));
                }}
                variant="ghost"
                alignSelf="flex-end">
                <EditIcon />
              </Button>
            </HStack>
          )}
          <Heading size="md" marginBottom={4}>
            Tags
          </Heading>
          <InputGroup marginBottom={4}>
            <InputLeftElement pointerEvents="none">
              <AddIcon color="gray.300" />
            </InputLeftElement>
            <Input
              type="text"
              placeholder="Add keywords"
              onKeyDown={handleKeywordInput}
            />
          </InputGroup>
          <HStack spacing={4} maxWidth="100%" flexWrap="wrap">
            {updatedFields.keywords === undefined
              ? data?.keywords?.map((label, index) => (
                  <Tag
                    size="lg"
                    key={label}
                    borderRadius="full"
                    variant="solid"
                    bg="chowdown.purple">
                    <TagLabel>{label}</TagLabel>
                    <TagCloseButton
                      onClick={() => handleRemoveKeyword(index)}
                    />
                  </Tag>
                ))
              : updatedFields.keywords?.map((label, index) => (
                  <Tag
                    size="lg"
                    key={label}
                    borderRadius="full"
                    variant="solid"
                    bg="chowdown.purple">
                    <TagLabel>{label}</TagLabel>
                    <TagCloseButton
                      onClick={() => handleRemoveKeyword(index)}
                    />
                  </Tag>
                ))}
          </HStack>

          <Button
            style={{ display: 'none' }}
            type="submit"
            isLoading={isSubmitting}
            ref={ref}>
            Save
          </Button>
        </Form>
      </FormControl>
    </>
  );
});

EateryDescriptionTag.displayName = 'EateryDescription';

export default EateryDescriptionTag;
