#!/bin/bash
docker-compose -f docker-compose-dev.yaml build
docker-compose -f docker-compose-dev.yaml up -d rabbitmq
sleep 20
docker-compose -f docker-compose-dev.yaml up -d producer consumer_post consumer_comment map_remove_columns reduce_agg_scores reduce_avg_scores filter_deleted_removed map_remove_columns_2 map_remove_columns_3 filter_body_student filter_score_mayor_avg map_remove_columns_4 reduce_agg_sentiment reduce_post_id find_max_sent_avg map_remove_columns_5 download_meme
docker-compose -f docker-compose-dev.yaml logs -f
