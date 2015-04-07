import mock
import time
import unittest2

from kafka.pykafka.consumer import SimpleConsumer, OwnedPartition


class TestSimpleConsumer(unittest2.TestCase):
    def test_consumer_partition_saves_offset(self):
        msgval = "test"
        op = OwnedPartition(None, None)

        message = mock.Mock()
        message.value = msgval
        message.offset = 20

        op.enqueue_messages([message])
        self.assertEqual(op.message_count, 1)
        message = op.consume()
        self.assertEqual(op.last_offset_consumed, message.offset)
        self.assertEqual(op.next_offset, message.offset + 1)
        self.assertNotEqual(message, None)
        self.assertEqual(message.value, msgval)

    def test_consumer_rejects_old_message(self):
        last_offset = 400
        op = OwnedPartition(None, None)
        op.last_offset_consumed = last_offset

        message = mock.Mock()
        message.value = "test"
        message.offset = 20

        op.enqueue_messages([message])
        self.assertEqual(op.empty, True)
        op.consume()
        self.assertEqual(op.last_offset_consumed, last_offset)

    def test_consumer_consume_empty_queue(self):
        op = OwnedPartition(None, None)

        message = op.consume()
        self.assertEqual(message, None)

    def test_consumer_offset_commit_request(self):
        topic = mock.Mock()
        topic.name = "test_topic"
        partition = mock.Mock()
        partition.topic = topic
        partition.id = 12345

        op = OwnedPartition(partition, None)
        op.last_offset_consumed = 200

        rqtime = int(time.time())
        request = op.build_offset_commit_request()

        self.assertEqual(request.topic_name, topic.name)
        self.assertEqual(request.partition_id, partition.id)
        self.assertEqual(request.offset, op.last_offset_consumed)
        # sketchy, but it works because of second resolution
        self.assertEqual(request.timestamp, rqtime)
        self.assertEqual(request.metadata, '')

    def test_consumer_offset_fetch_request(self):
        topic = mock.Mock()
        topic.name = "test_topic"
        partition = mock.Mock()
        partition.topic = topic
        partition.id = 12345

        op = OwnedPartition(partition, None)

        request = op.build_offset_fetch_request()

        self.assertEqual(request.topic_name, topic.name)
        self.assertEqual(request.partition_id, partition.id)

    def test_consumer_offset_counters(self):
        res = mock.Mock()
        res.offset = 400

        op = OwnedPartition(None, None)
        op.set_offset_counters(res)

        self.assertEqual(op.last_offset_consumed, res.offset)
        self.assertEqual(op.next_offset, res.offset + 1)


if __name__ == "__main__":
    unittest2.main()