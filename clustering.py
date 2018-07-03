import math as math
import operator
import random as rand

# import pkg_resources
# pkg_resources.require("matplotlib")
import matplotlib.pyplot as plt

from point import Point


class clustering:

    def __init__(self, geo_locs_, amount_of_clusters, lines_):
        self.geo_locations = geo_locs_
        self.lines_ = lines_
        self.amount_of_clusters = amount_of_clusters
        self.cluster_size = 0
        self.clusters = []  # clusters of nodes
        self.means = []  # means of clusters
        self.debug = False  # debug flag

    # this method returns the next random node
    def next_random(self, points, clusters):
        # pick next node that has the maximum distance from other nodes
        dist = {}
        for point_1 in points:
            # compute this node distance from all other points in cluster
            for cluster in clusters.values():
                point_2 = cluster[0]
                if point_1 not in dist:
                    dist[point_1] = math.sqrt(math.pow(point_1.latit - point_2.latit, 2.0) + math.pow(point_1.longit - point_2.longit, 2.0))
                else:
                    dist[point_1] += math.sqrt(math.pow(point_1.latit - point_2.latit, 2.0) + math.pow(point_1.longit - point_2.longit, 2.0))
        if self.debug:
            for key, value in dist.items():
                print("(%f, %f) ==> %f" % (key.latit, key.longit, value))

        # now let's return the point that has the maximum distance from previous nodes
        count_ = 0
        max_ = 0
        for key, value in dist.items():
            if count_ == 0:
                max_ = value
                max_point = key
                count_ += 1
            else:
                if value > max_:
                    max_ = value
                    max_point = key
        return max_point

    # this method computes the initial means
    def initial_means(self, points):
        # pick the first node at random
        point_ = rand.choice(points)
        if self.debug:
            print('point#0: %f %f' % (point_.latit, point_.longit))
        clusters = dict()
        clusters.setdefault(0, []).append(point_)
        points.remove(point_)
        # now let's pick k-1 more random points
        for i in range(1, self.amount_of_clusters):
            point_ = self.next_random(points, clusters)
            # clusters.append([point_])
            clusters.setdefault(i, []).append(point_)
            points.remove(point_)
        # compute mean of clusters
        self.means = self.compute_mean(clusters)
        if self.debug:
            print("initial means:")
            self.print_means(self.means)

    def compute_mean(self, clusters):
        means = []
        for cluster in clusters.values():
            mean_point = Point(0.0, 0.0)
            cnt = 0.0
            for point in cluster:
                mean_point.latit += point.latit
                mean_point.longit += point.longit
                cnt += 1.0
            mean_point.latit = mean_point.latit / cnt
            mean_point.longit = mean_point.longit / cnt
            means.append(mean_point)
        return means

    # this method assign nodes to the cluster with the smallest mean
    def assign_points(self, points):
        clusters = dict()
        for i in range(len(self.means)):
            clusters.setdefault(i, [])
        for point in points:
            dist = []
            centroids = []
            length = 0
            # find the best cluster for this node
            for mean in self.means:
                dist.append(math.sqrt(math.pow(point.latit - mean.latit, 2.0) + math.pow(point.longit - mean.longit, 2.0)))
            cnt_ = 0
            for d in dist:
                centroids.append((cnt_, d))
                cnt_ += 1
            centroids.sort(key = operator.itemgetter(1))

            for tuple in centroids:
                index = tuple[0]
                if len(clusters[index]) < self.cluster_size:
                    clusters.setdefault(tuple[0], []).append(point)
        return clusters

    def update_means(self, means, threshold):
        # check the current mean with the previous one to see if we should stop
        for i in range(len(self.means)):
            mean_1 = self.means[i]
            mean_2 = means[i]
            if math.sqrt(math.pow(mean_1.latit - mean_2.latit, 2.0) + math.pow(mean_1.longit - mean_2.longit,2.0)) > threshold:
                return False
        return True

    # debug function: print cluster points
    def print_clusters(self, clusters):
        cluster_cnt = 1
        for cluster in clusters.values():
            print('nodes in cluster {:d} {:d}'.format(cluster_cnt, len(cluster)))
            cluster_cnt += 1

    # print means
    def print_means(self, means):
        for point in means:
            print
            "{:f} {:f}".format(point.latit, point.longit)

    # calculate cluster size
    def calc_cluster_size(self):
        self.cluster_size = int(self.lines_ / self.amount_of_clusters) + 1

    def k_means(self, plot_flag):
        points_ = [point for point in self.geo_locations]
        # compute amount of clusters
        self.calc_cluster_size()
        # compute the initial means
        self.initial_means(points_)
        stop = False
        while not stop:
            # assignment step: assign each node to the cluster with the closest mean
            points_ = [point for point in self.geo_locations]
            clusters = self.assign_points(points_)
            means = self.compute_mean(clusters)
            stop = self.update_means(means, 0.01)
            if not stop:
                self.means = []
                self.means = means
        self.clusters = clusters

        # plot cluster for evluation
        if plot_flag:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            markers = ['o', 'd', 'x', 'h', 'H', 7, 4, 5, 6, '8', 'p', ',', '+', '.', 's', '*', 3, 0, 1, 2]
            colors = ['r', 'k', 'b', [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0],
                      [1, 1, 1]]
            cnt = 0
            for cluster in clusters.values():
                latits = []
                longits = []
                for point in cluster:
                    latits.append(point.latit)
                    longits.append(point.longit)
                ax.scatter(longits, latits, s=60, c=colors[cnt], marker=markers[cnt])
                cnt += 1
            plt.show()
        return 0