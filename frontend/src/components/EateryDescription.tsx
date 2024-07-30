import { forwardRef, useContext, useEffect, useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  HStack,
  Text,
  Textarea
} from '@chakra-ui/react';
import { AuthContext } from '../context/authContext';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getEateryDetails, updateEateryDetails } from '../utils/api/eateries';
import { Form } from 'react-router-dom';
import { CheckIcon, CloseIcon, EditIcon } from '@chakra-ui/icons';

const EateryDescription = forwardRef<HTMLButtonElement>((props, ref) => {
  const { getters } = useContext(AuthContext);
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [isCancelled, setIsCancelled] = useState<boolean>(false);
  const [error, setError] = useState('');
  const [description, setDescription] = useState<string>('');
  const [data, setData] = useState<EateryDetailsResponse>();
  useEffect(() => {
    // Fetch eatery details when the component mounts
    const fetchData = async () => {
      try {
        const details = await getEateryDetails(
          getters.sessionToken!,
          getters.userId!
        );
        setData(details);
        setDescription(details.description);
        console.log(details);
      } catch (error) {
        console.error('Error fetching eatery details:', error);
        setError('Error fetching eatery details');
      }
    };
    fetchData();
  }, [getters.sessionToken, getters.userId]);

  const { mutate } = useMutation({
    mutationFn: (updatedData: EateryUpdateDetailsRequest) =>
      updateEateryDetails(getters.sessionToken!, getters.userId!, updatedData),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['eatery', getters.userId]
      });
      setIsSubmitting(false);
      console.log('success');
    }
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log(description);
    if (description.length !== 0) {
      if (error) {
        return;
      }
      setIsSubmitting(true);

      console.log('description submitting');

      const updatedData: EateryUpdateDetailsRequest = {
        name: data?.name,
        email: data?.email,
        phone_number: data?.phone_number,
        manager_first_name: data?.manager_first_name,
        description: description,
        manager_last_name: data?.manager_last_name,
        keywords: data?.keywords
      };
      mutate(updatedData);
    }
  };

  const handleCancel = () => {
    setIsCancelled(true);
    setIsEditing(false);
  };

  const handleDone = () => {
    setIsCancelled(false);
    setIsEditing(false);
  };

  return (
    <>
      {isEditing ? (
        <FormControl>
          <Form onSubmit={handleSubmit}>
            <Textarea
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Edit Description"
            />
            <HStack>
              <Button onClick={handleCancel} variant="ghost">
                <CloseIcon />
              </Button>
              <Button onClick={handleDone} variant="ghost">
                <CheckIcon />
              </Button>
            </HStack>
            <Button
              style={{ display: 'none' }}
              type="submit"
              isLoading={isSubmitting}
              ref={ref}
              {...props}>
              Save
            </Button>
          </Form>
        </FormControl>
      ) : (
        <FormControl>
          <Form onSubmit={handleSubmit}>
            <HStack width="100%" justifyContent="space-between" align="top">
              <Box>
                {description !== '' ? (
                  <Text flexWrap="wrap">
                    {isCancelled ? data?.description : description}
                  </Text>
                ) : (
                  <Text color="chowdownPurple.400">No description yet</Text>
                )}
              </Box>

              <Button
                onClick={() => setIsEditing(true)}
                variant="ghost"
                alignSelf="flex-end">
                <EditIcon />
              </Button>
              <Button
                style={{ display: 'none' }}
                type="submit"
                isLoading={isSubmitting}
                ref={ref}
                {...props}>
                Save
              </Button>
            </HStack>
          </Form>
        </FormControl>
      )}
    </>
  );
});

EateryDescription.displayName = 'EateryDescription';

export default EateryDescription;
