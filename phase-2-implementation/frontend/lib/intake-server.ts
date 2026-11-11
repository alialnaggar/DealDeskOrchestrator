import 'server-only';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { type DealInputDTO, supportedMatch } from './intake-contract';

// Fail closed if an authoritative fixture changes without a reviewed matcher
// update. This checks the files actually used by the Python demo, not a client ID.
const fixtureHashes = {
  'm18_case_setup.py':'d1ffab448fb114aa9e2b5442f77c745ada03b4503380d37ee9985ae675f0ceee',
  'm21_integrated_credit_setup.py':'5c7c3b44af9f2ca54306980725ff2b8d0a119b541c4fc6b5bb98d615ceab7ddb',
};
export function matchAuthoritativeFixture(input:DealInputDTO) {
  for (const [file,expected] of Object.entries(fixtureHashes)) {
    const contents=readFileSync(resolve(process.cwd(),'../backend/tests',file));
    if (createHash('sha256').update(contents).digest('hex') !== expected) throw new Error('Authoritative fixture changed; manual matching disabled');
  }
  return supportedMatch(input);
}
export function inputDigest(input:DealInputDTO) { return createHash('sha256').update(JSON.stringify(input)).digest('hex'); }
