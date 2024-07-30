import React, { useContext } from 'react';
import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  ModalFooter,
  Heading,
  Button,
  Flex,
  Text,
  Textarea,
  Spacer,
  Checkbox,
  VStack,
  FormControl,
  FormErrorMessage
} from '@chakra-ui/react';
import { StarRatingInput } from '../StarRatingInput';
import { SubmitHandler, useForm } from 'react-hook-form';
import { AxiosError } from 'axios';
import { addEateryReview } from '../../utils/api/eateries';
import { AuthContext } from '../../context/authContext';
import { useMutation, useQueryClient } from '@tanstack/react-query';

type ReviewCreationFormProps = {
  voucherInstanceId: number;
  eateryId: number;
  onSubmitSuccess?: () => void;
  onSubmitError?: (err: unknown) => void;
};

type FormValues = {
  description: string;
  rating: '0' | '1' | '2' | '3' | '4' | '5';
  isAnonymous: boolean;
};

const defaultValues: FormValues = {
  description: '',
  rating: '0',
  isAnonymous: false
};

const ReviewCreationForm: React.FC<ReviewCreationFormProps> = ({
  onSubmitError,
  onSubmitSuccess,
  voucherInstanceId,
  eateryId
}) => {
  const {
    getters: { sessionToken }
  } = useContext(AuthContext);

  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (data: FormValues) =>
      addEateryReview(sessionToken!, eateryId, {
        description: data.description,
        anonymous: data.isAnonymous,
        rating: parseInt(data.rating),
        voucher_instance_id: voucherInstanceId
      }),
    onSuccess: () => {
      queryClient.invalidateQueries();
    }
  });

  const {
    handleSubmit,
    register,
    setError,
    setValue,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>();

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    try {
      await mutateAsync(data);

      onSubmitSuccess?.();
    } catch (e) {
      if (e instanceof AxiosError) {
        const error = e as AxiosError<{ detail: string }>;
        setError('root', { message: `${error.response?.data?.detail}` }); // TODO
      } else {
        console.error(e);
        setError('root', { message: 'Unknown error...' });
      }

      reset(defaultValues, { keepErrors: true });
      onSubmitError?.(e);
    }
  };

  const { name: ratingFieldName, onBlur: ratingFieldOnBlur } = register(
    'rating',
    {
      required: 'Please select a rating',
      validate: (v) =>
        ['1', '2', '3', '4', '5'].includes(v) || 'Please select a rating'
    }
  );

  return (
    <VStack gap="4" as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.description}>
        <Textarea
          placeholder="Review description..."
          resize="none"
          focusBorderColor="chowdownPurple.500"
          maxLength={400}
          rows={6}
          {...register('description', {
            required: 'A description is required',
            minLength: 1
          })}
        />
        <FormErrorMessage>{errors.description?.message}</FormErrorMessage>
      </FormControl>

      <Flex justifyContent="space-between" w="100%">
        <FormControl isDisabled={isSubmitting} isInvalid={!!errors.isAnonymous}>
          <Checkbox {...register('isAnonymous')}>Post Anonymously?</Checkbox>
          <FormErrorMessage>{errors.isAnonymous?.message}</FormErrorMessage>
        </FormControl>

        <FormControl isInvalid={!!errors.rating} w="min-content">
          <StarRatingInput
            name={ratingFieldName}
            onBlur={ratingFieldOnBlur}
            isDisabled={isSubmitting}
            onChange={(v) => setValue('rating', v)}
          />
          <FormErrorMessage textAlign="right" justifyContent="end">
            {errors.rating?.message}
          </FormErrorMessage>
        </FormControl>
      </Flex>

      {errors.root && (
        <Text variant="error" color="red">
          * {errors.root.message}
        </Text>
      )}

      <Spacer />

      <Button
        type="submit"
        borderRadius="full"
        colorScheme="chowdownGray"
        minWidth="40">
        Submit
      </Button>
    </VStack>
  );
};

type ReviewCreationModalProps = {
  isOpen: boolean;
  onClose: () => void;
  voucherName: string;
  voucherInstanceId: number;
  eateryId: number;
};

const ReviewCreationModal: React.FC<ReviewCreationModalProps> = ({
  isOpen,
  onClose,
  voucherName,
  voucherInstanceId,
  eateryId
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent mx={{ base: 2, md: 0 }}>
        <ModalCloseButton />
        <ModalHeader>
          <Heading color="chowdown.gray" fontSize="2xl" fontWeight="bold">
            Add a Review
          </Heading>
        </ModalHeader>
        <ModalBody>
          <Text as="span" fontSize="sm">
            Voucher:{' '}
            <Text as="i" fontWeight="semibold">
              &quot;{voucherName}&quot;
            </Text>
          </Text>

          <ReviewCreationForm
            voucherInstanceId={voucherInstanceId}
            eateryId={eateryId}
          />
        </ModalBody>
        <ModalFooter />
      </ModalContent>
    </Modal>
  );
};

export default ReviewCreationModal;
