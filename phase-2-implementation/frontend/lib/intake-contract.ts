import { z } from 'zod';

// Commercial inputs only. The backend owns stock, credit, policies and specialist
// evidence: a user must not be asked to invent these internal source records.
export const DealInput = z.object({
  customerId:z.string().trim().min(1,'Customer ID is required').max(100),
  dealId:z.string().trim().min(1,'Deal ID is required').max(100),
  productId:z.string().trim().min(1,'Product ID is required').max(100),
  lineId:z.string().trim().min(1,'Line ID is required').max(100),
  configuration:z.record(z.string(),z.unknown()),
  quantity:z.number().int('Quantity must be a whole number').positive('Quantity must be greater than zero').max(100000),
  requestedDeliveryDate:z.iso.date(),
  quotedUnitPrice:z.number().finite().positive('Unit price must be greater than zero').max(100000000),
  discountPercent:z.number().finite().min(0).max(100).nullable(),
  currencyCode:z.string().trim().min(1).max(10),
  paymentTermsDays:z.number().int().min(0).max(365),
  destinationCountryCode:z.string().trim().min(1).max(2),
  destinationRegion:z.string().trim().min(1).max(100),
  shippingServiceCode:z.string().trim().min(1).max(100),
  allowPartialDelivery:z.boolean(),
  catalogVersion:z.string().trim().min(1).max(100),
  policySetCode:z.string().trim().min(1).max(100),
  contractClauseCodes:z.array(z.string().trim().min(1).max(100)).max(10),
  additionalRequirements:z.string().trim().max(500),
}).strict();
export type DealInputDTO = z.infer<typeof DealInput>;

const common = {
  configuration:{},quantity:10,requestedDeliveryDate:'2026-09-04',quotedUnitPrice:900,
  discountPercent:null,currencyCode:'EUR',paymentTermsDays:30,
  destinationCountryCode:'DE',destinationRegion:'Berlin',shippingServiceCode:'standard',
  catalogVersion:'CATALOGUE_2026_V1',policySetCode:'BASELINE_2026',
  contractClauseCodes:['standard'],additionalRequirements:'',
};
// Exact supported commercial inputs from backend/tests/m18_case_setup.py:43,48,
// 133-148 and m21_integrated_credit_setup.py:27-40. No credit/stock is user input.
export const supportedInputs = {
  rc01:DealInput.parse({...common,customerId:'M18-C-B01',dealId:'M18-D-B01',productId:'M18-P-B01',lineId:'M18-L-B01',allowPartialDelivery:true}),
  uc02:DealInput.parse({...common,customerId:'M18-C-N01',dealId:'M18-D-N01',productId:'M18-P-N01',lineId:'M18-L-N01',allowPartialDelivery:false}),
} as const;

export function supportedMatch(input:DealInputDTO): 'rc01'|'uc02'|null {
  for(const key of ['rc01','uc02'] as const) {
    const expected=supportedInputs[key];
    if ((Object.keys(expected) as (keyof DealInputDTO)[]).every(field => JSON.stringify(input[field]) === JSON.stringify(expected[field]))) return key;
  }
  return null;
}
