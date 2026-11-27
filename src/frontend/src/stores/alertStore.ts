import { uniqueId } from "lodash";
import { create } from "zustand";
import type { AlertItemType } from "../types/alerts";
import type { AlertStoreType } from "../types/zustand/alert";
import { customStringify } from "../utils/reactflowUtils";

// Cap the notification history so a long session never grows unbounded.
const MAX_NOTIFICATIONS = 100;

const useAlertStore = create<AlertStoreType>((set, get) => ({
  errorData: { title: "", list: [] },
  noticeData: { title: "", link: "" },
  successData: { title: "" },
  notificationCenter: false,
  notificationList: [],
  tempNotificationList: [],
  addNotificationToHistory: (notification: Omit<AlertItemType, "id">) => {
    const newNotification = { ...notification, id: uniqueId() };
    const nextList = [newNotification, ...get().notificationList].slice(
      0,
      MAX_NOTIFICATIONS,
    );
    set({
      notificationCenter: true,
      notificationList: nextList,
    });
  },
  addNotificationToTempList: (notification: Omit<AlertItemType, "id">) => {
    const newNotification = { ...notification, id: uniqueId() };
    const tempList = get().tempNotificationList;
    if (
      !tempList.some((item) => {
        return (
          customStringify({
            title: item.title,
            type: item.type,
            list: item.list,
            link: item.link,
          }) ===
          customStringify({
            title: newNotification.title,
            type: newNotification.type,
            list: newNotification.list,
            link: newNotification.link,
          })
        );
      })
    ) {
      const nextList = [newNotification, ...get().tempNotificationList].slice(
        0,
        MAX_NOTIFICATIONS,
      );
      set({
        tempNotificationList: nextList,
      });
    }
  },
  setErrorData: (newState: { title: string; list?: Array<string> }) => {
    if (newState.title && newState.title !== "") {
      set({ errorData: newState });
      const notification: Omit<AlertItemType, "id"> = {
        type: "error",
        title: newState.title,
        list: newState.list,
      };
      get().addNotificationToHistory(notification);
      get().addNotificationToTempList(notification);
    }
  },
  setNoticeData: (newState: {
    title: string;
    link?: string;
    list?: Array<string>;
  }) => {
    if (newState.title && newState.title !== "") {
      set({ noticeData: newState });
      const notification: Omit<AlertItemType, "id"> = {
        type: "notice",
        title: newState.title,
        link: newState.link,
        list: newState.list,
      };
      get().addNotificationToHistory(notification);
      get().addNotificationToTempList(notification);
    }
  },
  setSuccessData: (newState: { title: string; list?: Array<string> }) => {
    if (newState.title && newState.title !== "") {
      set({ successData: newState });
      const notification: Omit<AlertItemType, "id"> = {
        type: "success",
        title: newState.title,
        list: newState.list,
      };
      get().addNotificationToHistory(notification);
      get().addNotificationToTempList(notification);
    }
  },
  setNotificationCenter: (newState: boolean) => {
    set({ notificationCenter: newState });
  },
  clearNotificationList: () => {
    set({ notificationList: [] });
  },
  removeFromNotificationList: (index: string) => {
    set({
      notificationList: get().notificationList.filter(
        (item) => item.id !== index,
      ),
    });
  },
  clearTempNotificationList: () => {
    set({ tempNotificationList: [] });
  },
  removeFromTempNotificationList: (index: string) => {
    set({
      tempNotificationList: get().tempNotificationList.filter(
        (item) => item.id !== index,
      ),
    });
  },
}));

export default useAlertStore;
