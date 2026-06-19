/// <reference types="next" />
/// <reference types="next/types/global" />

declare module "*.css" {
  const content: Record<string, string>;
  export default content;
}
