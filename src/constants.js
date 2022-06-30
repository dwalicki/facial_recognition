let DEBUG = false;
let host = 'http://127.0.0.1:8000';
let stripePublishKey = 'pk_test_MaMJmdWrhGRr6EwcDQBWbYos';

if (!DEBUG) {
    host = 'https://137.184.7.33';
    stripePublishKey = 'pk_test_MaMJmdWrhGRr6EwcDQBWbYos';
}

export { stripePublishKey };

export const APIEndpoint = `${host}/api`;

export const fileUploadUrl = `${APIEndpoint}/demo/`;
export const facialRecognitionURL = `${APIEndpoint}/upload/`;
export const userEmailURL = `${APIEndpoint}/email/`;
export const changeEmailURL = `${APIEndpoint}/change-email/`;
export const changePasswordURL = `${APIEndpoint}/change-password/`;
export const billingURL = `${APIEndpoint}/billing/`;
export const subscribeURL = `${APIEndpoint}/subscribe/`;
export const APIkeyURL = `${APIEndpoint}/api-key/`;
export const cancelSubscriptionURL = `${APIEndpoint}/cancel-subscription/`;
