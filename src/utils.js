import axios from 'axios';
import { APIEndpoint } from './constants';

export const authAxios = axios.create({
    baseURL: APIEndpoint,
    headers: {
        Authorization: {
            toString() {
                return `Token ${localStorage.getItem("token")}`;
            }
        }
    }
});
