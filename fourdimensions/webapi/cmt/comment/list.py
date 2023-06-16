from itertools import count
import json
import logging
import requests
from typing import List

from fourdimensions.webapi.const import DEFAULT_HEADER

# 参考格式 https://bcy.net/apiv3/cmt/reply/list?page=1&item_id=()&limit=15&sort=hot


class comment_list:

    class NoCommentError(Exception):
        pass

    @staticmethod
    def get(item_id: int, reply_id: int, page: int=1, sess: requests.Session = None):
        """ query https://bcy.net/apiv3/cmt/comment/list
        
        Args:
            item_id: 需要爬取评论的动态本身的编号
            item_id: 需要爬取评论的主楼本身的编号
            page: 楼中楼页码
        
        Returns:
            r.json()

        Raises:
            reply_list.NoCommentError: 未找到评论
        """

        url = "https://bcy.net/apiv3/cmt/comment/list"
        params = {
            "page": page,
            "item_id": item_id,
            "reply_id": reply_id
        }
        r = sess.get(url,params=params)
        r.raise_for_status()

        response_json: dict = r.json()
        assert response_json.get('code', -1) == 0, response_json.get('msg')

        return response_json
        # if response_json.get('data', {}).get('data'):
        #     return response_json
        
        # logging.info(f"{item_id} 下评论区 {reply_id} 的第 {page} 页没有评论")
        # raise comment_list.NoCommentError(f"{item_id} 下评论区 {reply_id} 的第 {page} 页没有评论")

    @staticmethod
    def get_all_comments(item_id: int, reply_id:int, sess: requests.Session = None):

        page = 1
        comments = []
        while True:
            print(page, end='\r')
            data = comment_list.get(item_id=item_id, reply_id=reply_id, page=page, sess=sess)
            if not data['data'].get('data'):
                break
            page += 1
            comments.extend(data['data']['data'])
        # assert len(item_ids) == len(set(item_ids))

        return comments



if __name__ == "__main__":
    sess = requests.session()
    sess.headers.update(DEFAULT_HEADER)
    try:
        reply = comment_list.get(7243752692219124791, 7243759733893989153, sess=sess, page=1)
    except comment_list.NoCommentError:
        print("该 item 没有评论")
    else:
        with open(__file__.replace(__file__.split("/")[-1], "comment_list-demo.json"), "w", encoding="utf-8") as f:
            json.dump(reply, f, indent=4, ensure_ascii=False)
    
    def loop_demo():
        sess = requests.session()
        sess.headers.update(DEFAULT_HEADER)
        replies: List[dict] = []
        for page in count(1):
            try:
                print(f"正在爬取第 {page} 页评论", end='\r')
                reply = comment_list.get(7243752692219124791, 7243759733893989153, sess=sess, page=page)
                replies.append(reply)
            except comment_list.NoCommentError:
                if page == 1:
                    print('此页无内容')
                else:
                    print("完成")
                    break
        
        return replies
    
    replies = loop_demo()
    with open(__file__.replace(__file__.split("/")[-1], "comment_list-loop-demo.json"), "w", encoding="utf-8") as f:
            json.dump(replies, f, indent=4, ensure_ascii=False)