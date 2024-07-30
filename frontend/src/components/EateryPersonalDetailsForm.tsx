import { forwardRef, useContext, useState } from 'react';
import {
  Alert,
  AlertIcon,
  Button,
  FormControl,
  FormLabel,
  HStack,
  Heading,
  Input,
  Text,
  VStack
} from '@chakra-ui/react';
import { AuthContext } from '../context/authContext';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getEateryDetails, updateEateryDetails } from '../utils/api/eateries';
import { Form } from 'react-router-dom';
import { EditIcon } from '@chakra-ui/icons';
import AddressInput from './AddressInput';

const EateryPersonalDetailsForm = forwardRef<HTMLButtonElement>(
  (props, ref) => {
    const { getters } = useContext(AuthContext);
    const queryClient = useQueryClient();
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

    const [showSuccess, setShowSuccess] = useState<boolean>(false);

    const [updatedFields, setUpdatedFields] =
      useState<EateryUpdateDetailsRequest>({});

    const [newIncomingPassword, setNewIncomingPassword] = useState<string>('');

    const [isEditing, setIsEditing] = useState<{ [key: string]: boolean }>({});

    const [emailError, setEmailError] = useState<string>('');
    const [phoneNumberError, setPhoneNumberError] = useState<string>('');
    const [passwordError, setPasswordError] = useState<string>('');

    const { data } = useQuery({
      queryKey: ['eatery', getters.userId!, 'details'],
      queryFn: async () => {
        try {
          const details = await getEateryDetails(
            getters.sessionToken!,
            getters.userId!
          );
          // TODO: dont set all these states
          return details;
        } catch (error) {
          console.error('Error fetching eatery details:', error);
          return null;
        }
      },
      enabled: !!getters.userId
    });

    const { mutate } = useMutation({
      mutationFn: (updatedData: EateryUpdateDetailsRequest) =>
        updateEateryDetails(
          getters.sessionToken!,
          getters.userId!,
          updatedData
        ),
      onSuccess: () => {
        console.log('successfully updated personal details');
        queryClient.invalidateQueries({
          queryKey: ['eatery', getters.userId]
        });
        setIsSubmitting(false);
        setShowSuccess(true);
        setTimeout(() => {
          setShowSuccess(false);
        }, 5500);
      }
    });

    const handleFieldChange = (
      fieldName: string,
      value: string | Record<string, string | number>
    ) => {
      setUpdatedFields((prevState) => ({
        ...prevState,
        [fieldName]: value
      }));
    };

    // checks new password matches first instance
    const handleChangePassword = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.value === newIncomingPassword && passwordError === '') {
        handleFieldChange('password', newIncomingPassword);
      } else {
        if (passwordError !== 'Invalid password') {
          setPasswordError('Passwords must match');
        }
      }
      setIsEditing((prevState) => ({
        ...prevState,
        password: false
      }));
    };

    const handleChangingPassword = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.value === newIncomingPassword && passwordError === '') {
        setPasswordError('');
      }
    };

    return (
      <>
        <FormControl>
          {showSuccess && (
            <Alert status="success">
              <AlertIcon />
              Changes have been saved!
            </Alert>
          )}
          <Form onSubmit={() => mutate(updatedFields)}>
            <Heading size="lg" marginBottom={4}>
              Edit personal details
            </Heading>

            <FormLabel>Eatery Name</FormLabel>
            {isEditing.name ? (
              <Input
                type="text"
                value={updatedFields.name ?? data?.name}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                onBlur={(e) => {
                  handleFieldChange('name', e.target.value);
                  setIsEditing((prevState) => ({
                    ...prevState,
                    name: false
                  }));
                }}
              />
            ) : (
              <HStack justifyContent="space-between">
                <Text>{updatedFields.name ?? data?.name}</Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      name: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}

            <FormLabel>Manager First Name</FormLabel>
            {isEditing.manager_first_name ? (
              <Input
                type="text"
                value={
                  updatedFields.manager_first_name ?? data?.manager_first_name
                }
                onChange={(e) =>
                  handleFieldChange('manager_first_name', e.target.value)
                }
                onBlur={(e) => {
                  handleFieldChange('manager_first_name', e.target.value);
                  setIsEditing((prevState) => ({
                    ...prevState,
                    manager_first_name: false
                  }));
                }}
              />
            ) : (
              <HStack justifyContent="space-between">
                <Text>
                  {updatedFields.manager_first_name ?? data?.manager_first_name}
                </Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      manager_first_name: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}

            <FormLabel>Manager Last Name</FormLabel>
            {isEditing.manager_last_name ? (
              <Input
                type="text"
                value={
                  updatedFields.manager_last_name ?? data?.manager_last_name
                }
                onChange={(e) =>
                  handleFieldChange('manager_last_name', e.target.value)
                }
                onBlur={(e) => {
                  handleFieldChange('manager_last_name', e.target.value);
                  setIsEditing((prevState) => ({
                    ...prevState,
                    manager_last_name: false
                  }));
                }}
              />
            ) : (
              <HStack justifyContent="space-between">
                <Text>
                  {updatedFields.manager_last_name ?? data?.manager_last_name}
                </Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      manager_last_name: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}

            <FormLabel>Email address</FormLabel>
            {isEditing.email ? (
              <Input
                type="text"
                value={updatedFields.email ?? data?.email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                onBlur={(e) => {
                  setIsEditing((prevState) => ({
                    ...prevState,
                    email: false
                  }));
                  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                  if (!emailRegex.test(e.target.value)) {
                    setEmailError('Invalid email address');
                    handleFieldChange('email', data?.email || '');
                  } else {
                    handleFieldChange('email', e.target.value);
                    setEmailError('');
                  }
                }}
              />
            ) : (
              <HStack justifyContent="space-between">
                <Text>{updatedFields.email ?? data?.email}</Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      email: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}
            {emailError && <Text color="red.500">{emailError}</Text>}

            <FormLabel>Phone Number</FormLabel>
            {isEditing.phone_number ? (
              <Input
                type="number"
                value={updatedFields.phone_number ?? data?.phone_number}
                onChange={(e) =>
                  handleFieldChange('phone_number', e.target.value)
                }
                onBlur={(e) => {
                  setIsEditing((prevState) => ({
                    ...prevState,
                    phone_number: false
                  }));
                  const phoneRegex =
                    /^\+?[0-9]{1,3}?[-\s.]?([(]?[0-9]{1,4}[)])?[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,9}$/;
                  if (!phoneRegex.test(e.target.value)) {
                    setPhoneNumberError(
                      'Must have 10 digits starting with "04"'
                    );
                  } else {
                    setPhoneNumberError('');
                  }
                }}
              />
            ) : (
              <HStack justifyContent="space-between">
                <Text>{updatedFields.phone_number ?? data?.phone_number}</Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      phone_number: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}
            {phoneNumberError && (
              <Text color="red.500">{phoneNumberError}</Text>
            )}

            <FormLabel>Address</FormLabel>
            {isEditing.address ? (
              <HStack>
                <Input
                  type="number"
                  width="15%"
                  maxLength={4}
                  value={
                    updatedFields.address?.unit_number ??
                    data?.address.unit_number
                  }
                  onChange={(e) => {
                    handleFieldChange('address', {
                      unit_number: e.target.value
                    });
                  }}
                />
                <AddressInput
                  onAddressChoice={(newAddress) => {
                    console.log(newAddress.formatted);
                    handleFieldChange('address', {
                      city: newAddress.city ?? '',
                      country: newAddress.country,
                      county: newAddress.county ?? '',
                      fmt_address: newAddress.formatted,
                      house_number: newAddress.house_no ?? '',
                      latitude: newAddress.lat,
                      longitude: newAddress.lon,
                      postcode: newAddress.postcode ?? '',
                      state: newAddress.state,
                      street: newAddress.street ?? '',
                      unit_number: updatedFields.address?.unit_number || ''
                    });
                    setIsEditing((prevState) => ({
                      ...prevState,
                      address: false
                    }));
                  }}
                />
              </HStack>
            ) : (
              <HStack justifyContent="space-between">
                <Text>
                  {updatedFields.address?.unit_number ??
                    data?.address.unit_number}{' '}
                  {updatedFields.address?.fmt_address ??
                    data?.address.formatted_str}
                </Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      address: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}

            <FormLabel>Change Password</FormLabel>
            {isEditing.password ? (
              <VStack>
                <Input
                  id="newPassword"
                  type="password"
                  placeholder="New password"
                  onChange={(e) => setNewIncomingPassword(e.target.value)}
                  onBlur={(e) => {
                    const passwordRegex =
                      /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@_$!%*?&]{8,}$/;
                    if (!passwordRegex.test(e.target.value)) {
                      setPasswordError('Invalid password');
                    } else {
                      console.log('no error');
                      setNewIncomingPassword(e.target.value);
                      setPasswordError('');
                    }
                  }}
                />
                <Input
                  id="confirmPassword"
                  type="password"
                  onChange={(e) => handleChangingPassword(e)}
                  onBlur={(e) => handleChangePassword(e)}
                  placeholder="Confirm new password"
                />
              </VStack>
            ) : (
              <HStack justifyContent="space-between">
                <Text>********</Text>
                <Button
                  onClick={() =>
                    setIsEditing((prevState) => ({
                      ...prevState,
                      password: true
                    }))
                  }
                  variant="ghost"
                  alignSelf="flex-end">
                  <EditIcon />
                </Button>
              </HStack>
            )}
            {passwordError && <Text color="red.500">{passwordError}</Text>}

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
      </>
    );
  }
);

EateryPersonalDetailsForm.displayName = 'EateryPersonalDetailsForm';

export default EateryPersonalDetailsForm;
