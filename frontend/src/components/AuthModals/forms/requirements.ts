import { RegisterOptions } from 'react-hook-form';

export const registration = {
  email: {
    required: 'Email is required.',
    pattern: {
      value: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b/,
      message: 'Email must be valid'
    }
  },
  password: {
    required: 'Password is required.',
    minLength: {
      value: 8,
      message: 'Passwords must be atleast 8 characters long'
    },
    pattern: {
      value: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@_$!%*?&]{8,}$/,
      message:
        'Password must contain atleast 1 number, 1 character, and only contain the symbols "@_$!%*?&"'
    }
  },
  abn: {
    required: 'ABN is required.',
    maxLength: { value: 11, message: 'ABN length must be 11 digits' },
    minLength: { value: 11, message: 'ABN length must be 11 digits' }
  },
  address: {
    required: 'Address is required.'
  },
  businessName: {
    required: 'Business Name is required.'
  },
  firstName: {
    required: 'First Name is required.'
  },
  lastName: {
    required: 'Last Name is required.'
  },
  phoneNumber: {
    required: 'Phone Number is required.',
    pattern: {
      value:
        /^\+?[0-9]{1,3}?[-\s.]?([(]?[0-9]{1,4}[)])?[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,9}$/,
      message: 'Phone number must be of valid form'
    }
  },
  unitNumber: {}
} satisfies Record<string, RegisterOptions>;

export const login = {
  email: {
    required: 'Email is required.'
  },
  password: {
    required: 'Password is required.'
  }
} satisfies Record<string, RegisterOptions>;
