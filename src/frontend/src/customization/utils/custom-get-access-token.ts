import { Cookies } from "react-cookie";
import { PRIMEAGENT_ACCESS_TOKEN } from "@/constants/constants";

export const customGetAccessToken = () => {
  const cookies = new Cookies();
  return cookies.get(PRIMEAGENT_ACCESS_TOKEN);
};
