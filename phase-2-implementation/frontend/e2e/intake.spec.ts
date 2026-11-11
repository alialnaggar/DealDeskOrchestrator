import { expect,test, type Page } from '@playwright/test';

async function fill(page:Page, code:'B01'|'N01') {
  for(const [field,value] of Object.entries({customerId:`M18-C-${code}`,dealId:`M18-D-${code}`,productId:`M18-P-${code}`,lineId:`M18-L-${code}`,quantity:'10',requestedDeliveryDate:'2026-09-04',quotedUnitPrice:'900'})) await page.locator(`#${field}`).fill(value);
  if(code==='N01') await page.getByLabel('Customer permits partial delivery').uncheck();
}

test('manual deal intake validates, rejects modified deals, edits and runs only exact supported cases',async({page})=>{
  test.setTimeout(220000);
  let launches=0;page.on('request',request=>{if(request.method()==='POST' && new URL(request.url()).pathname==='/api/assessments') launches++;});
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Start a Deal Assessment'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'System Capabilities & Validation'})).toBeVisible();
  await expect(page.getByRole('link',{name:'Explore Scenarios'})).toBeVisible();
  await expect(page.getByRole('button',{name:'CRM / Existing Deal — Coming Soon'})).toBeDisabled();
  await page.getByRole('link',{name:/Enter Deal Details/}).click();
  await page.getByRole('button',{name:/Review Deal Details/}).click();
  await expect(page.getByText('Customer ID is required.')).toBeVisible();
  await fill(page,'B01');
  await page.locator('#configuration').fill('not-json');await page.getByRole('button',{name:/Review Deal Details/}).click();
  await expect(page.getByText(/Enter configuration options as a JSON object/)).toBeVisible();
  await page.locator('#configuration').fill('{}');await page.locator('#quotedUnitPrice').fill('-1');
  await page.getByRole('button',{name:/Review Deal Details/}).click();await expect(page.getByText(/Unit price must be greater than zero/)).toBeVisible();
  await page.locator('#quotedUnitPrice').fill('901');await page.getByRole('button',{name:/Review Deal Details/}).click();
  await expect(page.getByRole('heading',{name:'Review & Confirm'})).toBeVisible();
  await expect(page.getByText('901',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:/Confirm & Check Support/}).click();
  await expect(page.getByRole('heading',{name:'Deal input not supported'})).toBeVisible();
  await expect(page.getByText(/not recorded or persisted/)).toBeVisible();
  expect(launches).toBe(0);
  await page.getByRole('button',{name:'Edit entries'}).click();await page.locator('#quotedUnitPrice').fill('900');
  await page.getByRole('button',{name:/Review Deal Details/}).click();
  await page.getByRole('button',{name:/Confirm & Check Support/}).click();
  await expect(page).toHaveURL(/\/scenarios\/rc01\?intake=/);
  await expect(page.getByRole('heading',{name:'Confirmed input matches this synthetic fixture'})).toBeVisible();
  await page.getByRole('button',{name:/Run Assessment/}).click();
  expect(launches).toBe(1);
  await expect(page).toHaveURL(/\/assessments\/[0-9a-f]{32}\?intake=/);
  await expect(page.getByText(/Manual intake matched the pinned B01\/RC01 fixture/)).toBeVisible();
  await expect(page.getByRole('heading',{name:'A later delivery needs the customer’s decision'})).toBeVisible({timeout:120000});
  await expect(page.getByRole('heading',{name:'Review, not authorization'})).toBeVisible();
  await page.goto('/intake');await fill(page,'N01');
  await page.getByRole('button',{name:/Review Deal Details/}).click();
  await expect(page.getByText('No',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:/Confirm & Check Support/}).click();
  await expect(page).toHaveURL(/\/scenarios\/uc02\?intake=/);
  await expect(page.getByRole('heading',{name:'Confirmed input matches this synthetic fixture'})).toBeVisible();
  await page.getByRole('button',{name:/Run Assessment/}).click();
  expect(launches).toBe(2);
  await expect(page.getByRole('heading',{name:'No verified candidate'})).toBeVisible({timeout:120000});
  await expect(page.locator('.timeline li')).toHaveCount(20);
});
