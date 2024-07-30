import { RegisterOptions } from 'react-hook-form';

export const creation = {
  name: { required: 'Voucher title is required' },
  description: { required: 'Voucher description is required' },
  conditions: { required: 'Voucher conditions are required' },
  quantity: {
    required: 'Voucher quantity is required',
    min: { value: 1, message: 'Voucher quantity must be greater than 0' },
    max: { value: 100, message: 'Voucher quantity must not exceed 100' }
  },
  expiry: {
    required: 'Voucher expiry date is required',
    valueAsDate: true,
    validate: (v) =>
      new Date() < v || 'Voucher expiry date must be in the future'
  },
  release: {
    required: 'Voucher release date is required',
    valueAsDate: true,
    validate: (v) =>
      new Date(new Date().getTime() - 5 * 60000) < v ||
      'Voucher release date must not be in the past'
  },
  schedule: {
    required: 'Voucher schedule is required',
    validate: (v) =>
      v === 'once' ||
      v === 'daily' ||
      v === 'weekly' ||
      v === 'fortnightly' ||
      v === 'monthly' ||
      'Voucher schedule must be proposed type'
  }
} satisfies Record<string, RegisterOptions>;
