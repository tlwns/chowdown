import React from 'react';
import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  VStack,
  Text
} from '@chakra-ui/react';
import { SubmitHandler, useForm } from 'react-hook-form';

import * as requirements from './requirements';
import { customerLogin } from '../../../utils/api/auth';
import { AxiosError } from 'axios';
import { CommonFormProps } from '../types';

type FormValues = {
  email: string;
  password: string;
};

const defaultValues: FormValues = {
  email: '',
  password: ''
};

const CustomerLoginForm: React.FC<CommonFormProps> = ({
  onSubmitError,
  onSubmitSuccess
}) => {
  const {
    handleSubmit,
    register,
    setError,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>();

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    try {
      const res = await customerLogin(data.email, data.password);
      onSubmitSuccess(res);
    } catch (e) {
      const error = e as AxiosError<{ detail: string }>;
      setError('root', { message: `${error.response?.data?.detail}` });
      reset(defaultValues, { keepErrors: true });
      onSubmitError(e);
    }
  };

  return (
    <VStack spacing="8" as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.email}>
        <FormLabel>Email</FormLabel>
        <Input
          {...register('email', requirements.login.email)}
          type="email"
          placeholder="customer@domain.com"
        />
        <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.password}>
        <FormLabel>Password</FormLabel>
        <Input
          {...register('password', requirements.login.password)}
          type="password"
          placeholder="Password"
        />
        <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
      </FormControl>

      {errors.root && (
        <Text variant="error" color="red">
          * {errors.root.message}
        </Text>
      )}

      <Button
        type="submit"
        colorScheme="chowdownLavender"
        borderRadius="full"
        isLoading={isSubmitting}>
        Login as Customer
      </Button>
    </VStack>
  );
};

export default CustomerLoginForm;
